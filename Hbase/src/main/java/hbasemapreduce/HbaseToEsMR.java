package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.hbase.mapreduce.TableReducer;
import org.apache.hadoop.io.ArrayWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.elasticsearch.hadoop.mr.EsOutputFormat;
import org.neo4j.driver.v1.Session;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.json.JSONArray;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;

import customcommon.BeanUtils;
import customcommon.StrUtils;
import hbaseextends.TextArrayWritable;
import neo4jclient.NeoDriver;
import static org.neo4j.driver.v1.Values.parameters;

import hbasemodels.BaseOP;
import hbasemodels.FunctionKeyWordOP;
import hbaseutils.HbaseDao;

import esmapreduce.configuration.HadoopConfiguration;

public class HbaseToEsMR {
	public static Logger LOG = LoggerFactory.getLogger(HbaseToEsMR.class);
	public static final String TABLENAME="functions";
	public static final String iCFAMILY="a";
	public static final String i_CONTENT = "content";
	public static final String i_SUBTITLE = "subTitle";
	public static final String i_TITLE = "title";
	
	public static class Mapper extends  TableMapper<NullWritable, Text> {
		
		private StrUtils strutils = null; 
		private Session neosession = null;
		
		@Override
		protected void setup(Context context){
			
			  strutils = new StrUtils();
			  
		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			String data_row_key = new String(value.getRow(),"utf8");
		 	
		 	ByteArrayInputStream content_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes()));
			String i_content =(String) BeanUtils.BytesToObject(content_stream);
		 	
			ByteArrayInputStream title_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_TITLE.getBytes()));
			String i_title =(String) BeanUtils.BytesToObject(title_stream);
		 	
			ByteArrayInputStream subtitle_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_SUBTITLE.getBytes()));
			String i_subTitle =(String) BeanUtils.BytesToObject(subtitle_stream);
		 	
		 	List<String> list_token = strutils.extractKeyWord(i_content,5);
		 	
		 	try {
//		 		NeoDriver neo = new NeoDriver();
//				neosession = neo.createSession();
//					 	
//			 	neo.runPutStatement("MERGE (a:FunctionsTitle {title:{title},uuid:{uuid}})",
//	                    parameters("title",i_title,"uuid",data_row_key) );
//			 	
//			 	for(String token:list_token){
//			 		neo.runPutStatement("MERGE (a:FunctionsWord {word: {word}})",
//	                        parameters("word", token));
//			 		
//			 		neo.runPutStatement("MATCH (a:FunctionsWord {word: {word}}),\n" +
//	                         "      (b:FunctionsTitle {title: {title}})\n" +
//	                         "MERGE (a)-[r:artilce_keyword_in_title]->(b)\n" ,
//	                parameters("word",token,"title",i_title) );
//			 		
//				  	
//			 	}
//			 	System.out.println(data_row_key);
//			 	neo.destoryDriver();
			 	
			 	String source =  "{"+
							"\"title\":\""+i_title+"\"," +
							"\"subTitle\":\""+i_subTitle+"\"," +
							"\"uuid\":\""+data_row_key+"\","+
							"\"content\":\""+i_content+"\""+
							"}";
			 	System.out.println(source);
	 		    Text jsonDoc = new Text(source);
			 	context.write(NullWritable.get(), jsonDoc);
			 	
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
		
		@Override
		 protected void cleanup(Context context){
			
			this.strutils = null;
		}
	}
		
  
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException, ClassNotFoundException, InterruptedException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);

			   String[] fields = {i_CONTENT,i_SUBTITLE,i_TITLE};
			   conf.setStrings("index.fields", fields);
			   conf.set("es.nodes", "gx.master");
			   conf.set("es.port", "9202"); 
			   conf.set("es.index.auto.create", "yes");
			   conf.set("es.resource", "functions/articles");
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
			   
			   job.setJobName("HbaseToEsMR_"+date);
			   job.setJarByClass(HbaseToEsMR.class);
			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			

}
