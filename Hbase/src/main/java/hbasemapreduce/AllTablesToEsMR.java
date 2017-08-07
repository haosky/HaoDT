package hbasemapreduce;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.elasticsearch.hadoop.mr.EsOutputFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import customcommon.StrUtils;
import mongotablesv1.MongoDB2Hbase;

public class AllTablesToEsMR {
	public static Logger LOG = LoggerFactory.getLogger(AllTablesToEsMR.class);
	public static final String TABLENAME="ALLTABLES";
	public static final String iCFAMILY="a";

	public static class Mapper extends  TableMapper<NullWritable, Text> {
		public static Log logmap = LogFactory.getLog(TableMapper.class);
		@Override
		protected void setup(Context context){
			
			  
		}
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			String data_row_key = new String(value.getRow(),"utf8");
			System.out.println(data_row_key);
			String source = "";
			try {

			 	String[] cols = data_row_key.split("::")[0].split(":");	
			 	String esid = StrUtils.toMd5Str(data_row_key);
//			 	System.out.println(esid);
//			 	System.out.println("---------------------");
				StringBuilder sb = new StringBuilder();
				ArrayList<String> keywords = new ArrayList<String>();
				StringBuilder kb = new StringBuilder();
				for(String s : cols){
					//列对应值
								
					String v = null;
					List<Cell> cr =value.getColumnCells(iCFAMILY.getBytes(), s.getBytes());
					for(Cell c :cr){
						String cv = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength(),"utf8");
						if(! cv.trim().toLowerCase().equals("null")){
							v = cv;
						}
						break;
					}
					
					//列对应中文名称
					String cloumn_name = null;
					
					List<Cell> crc =value.getColumnCells(iCFAMILY.getBytes(), (s+"__STR").getBytes());
					for(Cell c :crc){
						cloumn_name = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength(),"utf8");
						break;
					}
					
					//列对应中文描述
					String cloumn_comments = null;

					List<Cell> crs = value.getColumnCells(iCFAMILY.getBytes(), (s+"__COMMENTS").getBytes());
					for(Cell c :crs){
						cloumn_comments = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength(),"utf8");
						break;
					}
					
					//列对应的所包含的关键字
					String cloumn_keywords =  "[]";
					
					List<Cell> crk = value.getColumnCells(iCFAMILY.getBytes(), (s+"__KEYWORDS").getBytes());
					for(Cell c :crk){
						cloumn_keywords = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength(),"utf8");
						break;
					}
					
					
					if(cloumn_keywords.length() > 8 && cloumn_keywords.contains(",")){
//						cloumn_keywords = cloumn_keywords
						cloumn_keywords = cloumn_keywords.replace("[", "").replace("]", "");
						for(String str : cloumn_keywords.split(",")){
							str = str.trim();
							String strin = "\""+str.trim()+"\"";
							if(keywords.contains(strin))
								continue;
							keywords.add(strin);
							kb.append(str+",");
						}
					}

					sb.append("\""+s+"\":"+(v == null || v.trim().toLowerCase().equals("null")?"\"\"":"\""+v.replaceAll("\n", "\\\\n").replaceAll("\r", "\\\\n")+"\"")+",");
					sb.append("\""+s+"__STR\":"+(cloumn_name == null || cloumn_name.trim().toLowerCase().equals("null")?"\"\"":"\""+cloumn_name.replaceAll("\n", "\\\\n").replaceAll("\r", "\\\\n")+"\"")+",");
					sb.append("\""+s+"__COMMENTS\":"+(cloumn_comments == null || cloumn_comments.trim().toLowerCase().equals("null")?"\"\"":"\""+cloumn_comments.replaceAll("\n", "\\\\n").replaceAll("\r", "\\\\n")+"\"")+",");

				}
				sb.append("\"keywords_str\":\""+kb.toString().replace("\"", "").replace("\'", "")+"\",");
				source = "{\"_uuid\":\""+esid+"\","+sb.toString()+"\"KEYWORDOBJ\":"+keywords.toString()+"}";
	 		    try{
	 		    	Text jsonDoc = new Text(source);
	 		    	context.write(NullWritable.get(), jsonDoc);
	 		    }catch (Exception e) {
					// TODO Auto-generated catch block
	 		    	System.out.println(e.getMessage());
	 		    	logmap.error(e.getMessage());
	 		    	logmap.error(source);
				}
			 	
		 	} catch (Exception e) {
				// TODO Auto-generated catch block
		 		System.out.println(e.getMessage());
		 		logmap.error(e.getMessage());
		 		logmap.error(source);
			}
		 			  	
		}
		
		@Override
		 protected void cleanup(Context context){
			
		}
	}
		
  
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException, ClassNotFoundException, InterruptedException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);
			   	
			   conf.set("es.nodes", "gx.master");
			   conf.set("es.port", "9202"); 
			   
//			   conf.set("es.index.auto.create", "yes");
			   conf.set("es.mapping.id", "_uuid");
			   conf.set("es.resource", "gdfinanical/alldata");
			   conf.set("es.input.json", "yes"); 
			   Job job = Job.getInstance(conf);

			   Scan scan = new Scan();
//			   scan.setFilter(filter1);

			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			   
			   
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
					   NullWritable.class,         
			           Text.class,
			           job);     
			   Date date = new Date();
			   job.setMapOutputValueClass(Text.class); 
			   job.setOutputFormatClass(EsOutputFormat.class);
			   
			   job.setJobName("AlltablesHbaseToEsMR_"+date);
			   job.setJarByClass(AllTablesToEsMR.class);
			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			

}
