package textextraction.word;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

import org.apache.poi.POIOLE2TextExtractor;
import org.apache.poi.extractor.ExtractorFactory;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.xwpf.extractor.XWPFWordExtractor;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.poifs.filesystem.POIFSFileSystem;
import org.apache.xmlbeans.XmlException;

public class Word2Text {
	
	 

	
	public static String extract(File inputFile) throws IOException, OpenXML4JException, XmlException{
		FileInputStream fis = new FileInputStream(inputFile);
		String[] paragraphText = null;
		if(inputFile.getName().endsWith(".doc")){
		  POIFSFileSystem fileSystem = new POIFSFileSystem(fis);
//		  POIOLE2TextExtractor oleTextExtractor = 
//				   ExtractorFactory.createExtractor(fileSystem);
		  
		  WordExtractor wordExtractor = new WordExtractor(fileSystem);
	      paragraphText = wordExtractor.getParagraphText();
	      fileSystem.close();
	      wordExtractor.close();
		}
		else{
			
			XWPFDocument doc = new XWPFDocument(fis); 
	        XWPFWordExtractor extractor = new XWPFWordExtractor(doc);
	        paragraphText = extractor.getText().split("\n");
	        
		}	
      StringBuffer textbuff = new StringBuffer();
      for (String paragraph : paragraphText) {
          String p = paragraph.replaceAll("", "");
          if(p.replaceAll("\n", "").trim().length() > 0){
        	  textbuff.append(p);
          }
      }
      fis.close();
      
      return textbuff.toString();
   }

}
