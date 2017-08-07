package lumag.chm;

import lumag.util.BasicReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public abstract class CommonReader {
	public static Logger LOG = LoggerFactory.getLogger(CommonReader.class);
	private static final int GUID_LENGTH = 16;
	private static final byte[] HEADER_FILE = {'I', 'T', 'S', 'F'};
	private static final byte[] HEADER_FILE_SECTION = {(byte) 0xfe, 0x01, 0x00, 0x00};
	private static final int SECTION_FILE_SIZE = 0;
	protected static final int SECTION_INDEX = 1;

	private static final String CONTENT_UNCOMPRESSED = "Uncompressed";
	private static final String FILE_NAME_LIST = "::DataSpace/NameList";
	private static final String FILE_TRANSFORM_LIST = "::DataSpace/Storage/%s/Transform/List"; 
	private static final String FILE_CONTROL_DATA = "::DataSpace/Storage/%s/ControlData";
	private static final String FILE_CONTENT = "::DataSpace/Storage/%s/Content";
	private static final String FILE_TRANSFORM_INSTANCE_DATA = "::DataSpace/Storage/%s/Transform/%s/InstanceData/";
	private static final byte[] LZXC_BAD_GUID = 
			new byte[] {'{', 0, '7', 0, 'F', 0, 'C', 0, '2', 0, '8', 0, '9', 0, '4', 0, '0', 0, '-', 0,
						'9', 0, 'D', 0, '3', 0, '1', 0, '-', 0, '1', 0, '1', 0, 'D', 0, '0', 0}; 
	private static final byte[] LZXC_GUID = new byte[] {
		0x40, (byte) 0x89, (byte) 0xC2, 0x7F,
		0x31, (byte) 0x9D,
		(byte) 0xD0, 0x11,
		(byte) 0x9B, 0x27, 0x00, (byte) 0xA0, (byte) 0xC9, 0x1E, (byte) 0x9C, 0x7C  
	};

	private class Content {
		private final String name;
		private IDataStorage storage;

		public Content(String name,
				IDataStorage reader) {
			this.name = name;
			this.storage = reader;
		}
		
		@Override
		public String toString() {
			return name;
		}
		
		public String getName() {
			return name;
		}
	}
	
	private class ListingEntry {
		public final String name;
		public final int section;
		public final long offset;
		public final long length;

		public ListingEntry(final String name, final int section, final long offset, final long length) {
			this.name = name;
			this.section = section;
			this.offset = offset;
			this.length = length;
		}
		
		@Override
		public String toString() {
			return "File '" + name + "'" +
				" is at section " + section +
				" offset " + offset +
				" length " + length; 
		}
	}

	@SuppressWarnings("unused")
	private long fileSize;
	protected long dataOffset;

	private long[] sectionOffsets;
	private long[] sectionLengths;
	
	private Content[] content;

	private Map<String, ListingEntry> listing = new LinkedHashMap<String, ListingEntry>();
	protected BasicReader reader;
	
	protected CommonReader(RandomAccessFile input) {
		reader = new BasicReader(input);
	}

	protected void readFormatHeader() throws IOException, FileFormatException {
		checkHeader(HEADER_FILE);
		
		int version = reader.readDWord();
		if (version != 4 && version != 3 && version != 2) {
			throw new FileFormatException("ITSF Version " + version + " is unsupported");
		}

		int headerLen = reader.readDWord();
		if ((version == 2 && headerLen != 0x58) || 
			(version == 3 && headerLen != 0x60) ||
			(version == 4 && headerLen != 0x20)) {
			throw new FileFormatException("bad section length");
		}
		
		reader.readDWord(); // 1
		
		if (version == 4) {
			dataOffset = reader.readQWord();
		}
		
		reader.readDWord(); // time
		
		reader.readDWord(); // LCID
		
		if (version == 2 || version == 3) {
			reader.readGUID();
			reader.readGUID();
		
		
			readSectionTable(2);
		}
		
		if (version == 2) {
			dataOffset = sectionOffsets[SECTION_INDEX] + sectionLengths[SECTION_INDEX];
		} else if (version == 3) {
			dataOffset = reader.readQWord();
		}
	}

	protected void readSectionTable(int size) throws IOException {
		sectionOffsets = new long[size];
		sectionLengths = new long[size];
		
		for (int i = 0; i < size; i++) {
			sectionOffsets[i] = reader.readQWord();
			sectionLengths[i] = reader.readQWord();
		}
		
	}

	protected long getSectionOffset(int section) {
		return sectionOffsets[section];
	}

	protected long getSectionLengths(int section) {
		return sectionLengths[section];
	}

	protected void readFileSizeSection() throws FileFormatException, IOException {
		reader.seek(sectionOffsets[SECTION_FILE_SIZE]);
		checkHeader(HEADER_FILE_SECTION);
	
		if (sectionLengths[SECTION_FILE_SIZE] < 0x18) {
			throw new FileFormatException("FileSize section is too small");
		} else if (sectionLengths[SECTION_FILE_SIZE] > 0x18) {
			System.out.format("Warning: extra %d bytes at the end of FileSize section%n", sectionLengths[SECTION_FILE_SIZE] - 0x18);
		}
	
		int unk = reader.readDWord(); // mostly 0. One file with 1
		if (unk != 0) {
			LOG.warn("Warning: unknown element expected to be zero: " + unk);
		}
		fileSize = reader.readQWord();
	
		reader.readDWord(); // 0
		reader.readDWord(); // 0
	
	}

	protected void readListingEntries(long endPos) throws IOException {
			while (reader.getOffset() < endPos) {
				String name = reader.readString();
				int section = (int) reader.readCWord();
				long offset = reader.readCWord();
				long len = reader.readCWord();
				listing.put(name, new ListingEntry(name, section, offset, len));
			}
		}

	protected void readContentData() throws IOException, FileFormatException {
		ListingEntry nameList = listing.get(FILE_NAME_LIST);
	
		reader.seek(dataOffset + nameList.offset);
	
		short len = reader.readWord();
		if (len * 2 != nameList.length) {
			throw new FileFormatException("Incorrect " + FILE_NAME_LIST + " length");
		}
		
		short entries = reader.readWord();

		content = new Content[entries];
		
		for (int i = 0; i < entries; i++) {
			short nameLen = reader.readWord();
			char[] name = new char[nameLen];
			for (int j = 0; j < nameLen; j++) {
				name[j] = (char) reader.readWord();
			}
			reader.readWord(); // terminal zero
			String sName = new String(name);
			IDataStorage data;
			if (i == 0) {
				data = new DirectStorage(reader, dataOffset, fileSize - dataOffset);
			} else {
				Formatter fmt = new Formatter();
				fmt.format(FILE_CONTENT, sName);
				ListingEntry entry = listing.get(fmt.toString());
				fmt.close();
				
				if (entry == null) {
					throw new FileFormatException("No Content for " + sName);
				}

				data = new DirectStorage(reader, dataOffset + entry.offset, entry.length);
			}
			content[i] = new Content(sName, data);
		}
		
		for (Content cnt: content) {
			String name = cnt.getName();
			if (CONTENT_UNCOMPRESSED.equals(name)) {
				continue;
			}
			
			Formatter fmt;

			fmt = new Formatter();
			fmt.format(FILE_CONTROL_DATA, name);
			byte[] controlData = getFile(fmt.toString());
			fmt.close();
			BasicReader cdReader = new BasicReader(controlData);
			
			fmt = new Formatter();
			fmt.format(FILE_TRANSFORM_LIST, name);
			byte[] transforms = getFile(fmt.toString());
			fmt.close();

			if (Arrays.equals(transforms, LZXC_BAD_GUID)) {
				transforms = LZXC_GUID;
			}
			
			BasicReader trRreader = new BasicReader(transforms);
			
			for (int i = 0; i < transforms.length / GUID_LENGTH; i++) {
				int cdSize = cdReader.readDWord();
				byte[] cd = cdReader.read(cdSize * 4);
				
				String guid = trRreader.readGUID();

				Map<String, byte[]> files = new HashMap<String, byte[]>();
				fmt = new Formatter();
				fmt.format(FILE_TRANSFORM_INSTANCE_DATA, name, guid);
				String prefix = fmt.toString();
				int prefixLen = prefix.length();
				fmt.close();

				for (ListingEntry entry: listing.values()) {
					if (entry.name.startsWith(prefix)) {
						files.put(entry.name.substring(prefixLen), getFile(entry));
					}
				}

				ITransformation transform;
				if (guid.equals("{0A9007C6-4076-11D3-8789-0000F8105754}") ||
				    guid.equals("{7FC28940-9D31-11D0-9B27-00A0C91E9C7C}")) {
					transform = new LZXCTransformation();
				} else if (guid.equals("{67F6E4A2-60BF-11D3-8540-00C04F58C3CF}")) {
					transform = new MsDesTransformation();
				} else {
					continue;
				}
				transform.init(this, cnt.storage , guid, cd, files);
				cnt.storage = transform;
			}
			trRreader.close();
			cdReader.close();
		}
	}
	
	public ListingEntry getFileEntry(String name) {
		return listing.get(name);
	}

	public Collection<ListingEntry> getFiles() {
		return Collections.unmodifiableCollection(listing.values());
	}
	
	public byte[] getFile(String name) throws IOException, FileFormatException {
		ListingEntry entry = getFileEntry(name);
		
		if (entry == null) {
			throw new FileNotFoundException();
		}

		return getFile(entry);
	}

	private byte[] getFile(ListingEntry entry) throws FileFormatException {
		return content[entry.section].storage.getData(entry.offset, (int) entry.length);
	}

	private static boolean outFileNameRegex(String inputName,String regex){
		Pattern pattern = Pattern.compile(regex);
		Matcher matcher = pattern.matcher(inputName);
		return matcher.matches();
	}

	public void dump(String path,String title) throws IOException, FileFormatException {
		File parent = new File(path);
		parent.mkdirs();
		for (ListingEntry entry: getFiles()) {
			String fineName =  "/"+title+entry.name.replace(':', '_').replace("/","");
			if(!outFileNameRegex(fineName,"[/]?.*_[\\d]+\\.htm[l]?")){
				continue;
			}
			File f = new File(parent,fineName);
			File parentFile = f.getParentFile();
			if (!parentFile.exists()) {
				parentFile.mkdirs();
			}
			if (entry.name.charAt(entry.name.length() - 1) == '/') {
				f.mkdir();
				// FIXME
			} else {
				byte[] data = getFile(entry.name);
				OutputStream output = new BufferedOutputStream(new FileOutputStream(f));
				output.write(data);
				output.close();
			}
		}
	}

	protected void checkHeader(byte[] header) throws FileFormatException, IOException {
		byte[] data = reader.read(header.length);
		
		if (!Arrays.equals(data, header)) {
			throw new FileFormatException("Incorrect section header");
		}
	}

}
