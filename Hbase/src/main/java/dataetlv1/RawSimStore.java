package dataetlv1;

import java.io.BufferedReader;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import org.apache.hadoop.hbase.client.Put;
import org.gx.intell.Query.ContentSimQuery;

import customcommon.FileUtils;
import customcommon.StrUtils;
import hbaseutils.HbaseDao;

public class RawSimStore {
	
	public void readAndStore() throws IOException, NoSuchAlgorithmException{
		BufferedReader bff = FileUtils.getFile2BuffRead("D:\\迅雷下载\\flfg_content.csv");
		String str = null;
		bff.readLine();
		str = bff.readLine() ;
    	int line = 0;
    	Boolean isNotContent = true;
    	HbaseDao hdao = new HbaseDao();
    	int putline = 1000;
    	List<Put> puts = new ArrayList<Put>();
    	while(str !=null){
	    		try{
	    		
//	    		System.out.println(str);
	    		StringBuffer content_buff = new StringBuffer();
	    		String cols[] = str.split("	");    		
	    		String id = cols[0];
	    		String type = cols[1];
	    		String parentsname = cols[2];
	    		String parentname = cols[3];
	    		String code2name = cols[4];
	    		String bt = cols[5];
	    		String flfgbh = cols[6];
	    		String bbrq = cols[7];
	    		String ssrq = cols[8];
	    		String sxrq = cols[9];
	    		String bbdw = cols[10];
	    		content_buff.append(cols[11]);
	    		String tmpstr = null;
	    		while(isNotContent){
	    			tmpstr = bff.readLine();
	    			if(tmpstr.startsWith("\\")){
	    				content_buff.append("\n"+bff.readLine());
	    			}else{
	    				isNotContent=false;
	    				str =tmpstr;
	    			}
	    		}
	    		isNotContent = true;
	    		String content = content_buff.toString();
	     		String hd5findename = StrUtils.toMd5Str(id);
	     		ContentSimQuery cq = new ContentSimQuery();
	     		String simhash = cq.getConentSimHash(content);
	     		cq.destory();
				Put p = new Put((simhash+hd5findename).getBytes());
				Random r = new Random();
				int finical =(int)(r.nextDouble() * 10000);
				p.addColumn("a".getBytes(), "project".getBytes(), bt.getBytes());
				p.addColumn("a".getBytes(), "finical_unit".getBytes(), parentname.getBytes());
				p.addColumn("a".getBytes(), "finical_name".getBytes(), code2name.getBytes());
				p.addColumn("a".getBytes(), "date".getBytes(), sxrq.getBytes());
				p.addColumn("a".getBytes(), "doc".getBytes(), flfgbh.getBytes());
				p.addColumn("a".getBytes(), "content".getBytes(), content.getBytes());
				p.addColumn("a".getBytes(), "unit".getBytes(), parentsname.getBytes());
				p.addColumn("a".getBytes(), "finical".getBytes(), (finical+"").getBytes()); 
				p.addColumn("a".getBytes(), "simhash".getBytes(),simhash.getBytes()); 
				p.addColumn("a".getBytes(), "fl_type".getBytes(),type.getBytes()); 
				p.addColumn("a".getBytes(), "bbdw".getBytes(),bbdw.getBytes()); 
				
				puts.add(p);
				if(line >= putline){
					try{
						hdao.put("CaiZhengMoNiSim", puts);
						puts = new ArrayList<Put>();
						line = 0;
						System.out.println("hbase put----------------------------");
					}catch(Exception e){
						e.printStackTrace();
					}
				}
	    		content_buff = null;
	    		line +=1;
	    		System.out.println(line+"------------");
	    	}catch(Exception e){
				e.printStackTrace();
				System.out.println(str);
				str = bff.readLine();
				
			}
    	}
    	try{
			hdao.put("CaiZhengMoNiSim", puts);
			puts = new ArrayList<Put>();
		}catch(Exception e){
			e.printStackTrace();
		}finally{
			hdao.destory();
		}
    }
	
	public static void main(String args[]) throws NoSuchAlgorithmException, IOException{
		new RawSimStore().readAndStore();
	}
}
