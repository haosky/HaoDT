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
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.neo4j.driver.v1.Session;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.json.JSONArray;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;

import customcommon.BeanUtils;
import customcommon.StrUtils;
import hbaseextends.TextArrayWritable;
import neo4jclient.NeoDriver;
import static org.neo4j.driver.v1.Values.parameters;

import hbasemodels.BaseOP;
import hbasemodels.FunctionKeyWordOP;
import hbaseutils.HbaseDao;;


public class FunctionsKeyWordsMR {
	public static Logger LOG = LoggerFactory.getLogger(FunctionsKeyWordsMR.class);
	public static final String TABLENAME="functions";
	public static final String iCFAMILY="a";
	public static final String i_CONTENT = "content";
	public static final String i_SUBTITLE = "subTitle";
	public static final String i_TITLE = "title";
	
	public static class Mapper extends  TableMapper<Text, TextArrayWritable> {
		
		private StrUtils strutils = null; 
		private Session neosession = null;
		private HbaseDao hbasedao = null;
		
		@Override
		protected void setup(Context context){
			
			  strutils = new StrUtils();
			  
			  
			  hbasedao = new HbaseDao();
			  
		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			String data_row_key = new String(value.getRow());
		 	
		 	ByteArrayInputStream content_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes()));
			String i_content =(String) BeanUtils.BytesToObject(content_stream);
		 	
			ByteArrayInputStream title_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_TITLE.getBytes()));
			String i_title =(String) BeanUtils.BytesToObject(title_stream);
		 	
			ByteArrayInputStream subtitle_stream =new ByteArrayInputStream(value.getValue(iCFAMILY.getBytes(), i_SUBTITLE.getBytes()));
			String i_subTitle =(String) BeanUtils.BytesToObject(subtitle_stream);
		 	
		 	List<String> list_token = strutils.extractKeyWord(i_content,5);
		 	
		 	try {
		 		NeoDriver neo = new NeoDriver();
				neosession = neo.createSession();
					 	
			 	neo.runPutStatement("MERGE (a:FunctionsTitle {title:{title}})",
	                    parameters("title",i_title) );
			 	
			 	for(String token:list_token){
			 		neo.runPutStatement("MERGE (a:FunctionsWord {word: {word}})",
	                        parameters("word", token));
			 		
			 		neo.runPutStatement("MATCH (a:FunctionsWord {word: {word}}),\n" +
	                         "      (b:FunctionsTitle {title: {title}})\n" +
	                         "MERGE (a)-[r:artilce_keyword_in_title]->(b)\n" ,
	                parameters("word",token,"title",i_title) );
			 		
			 		
			 		String[] arryTest = {
				 			i_title,
				 			i_subTitle,
				 			token,
				 			data_row_key
				 	};
			 		
				 	TextArrayWritable textSets = new TextArrayWritable(arryTest);
				  	context.write(new Text(token),textSets);
			 	}
			 	System.out.println(data_row_key);
			 	neo.destoryDriver();
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 	//hbase 插入关键字字段
		 	FunctionKeyWordOP funkwop = new FunctionKeyWordOP();
		 	funkwop.setTitle(i_title);
		 	funkwop.setSubTitle(i_subTitle);
		 	JSONArray tag_json = new JSONArray();
		 	tag_json.put(list_token);
		 	funkwop.setKeyWords(tag_json.toString());
	        ArrayList<BaseOP> listPut = new ArrayList<BaseOP>();
		 	listPut.add(funkwop);
		 	try {
	            hbasedao.putByTableObject(listPut,"functions");
	        }catch (Exception e){e.printStackTrace();}
		 			  	
		}
		
		@Override
		 protected void cleanup(Context context){
			
			this.strutils = null;
			 hbasedao.destory();
		}
	}
		
 
	public static class Reducer extends TableReducer<Text,TextArrayWritable,ImmutableBytesWritable>{
		
		private HashMap<String,Integer> dictionary = null;
		private int keyword_total_count = 0;
		private HashMap<String,Integer> idf_count = null;
		
		@Override
		protected void setup(Context context){
			dictionary = new HashMap<String,Integer>();
		}
		
		@Override
		protected void reduce(Text key, Iterable<TextArrayWritable> values, Context context) throws IOException, InterruptedException {
			
			
		    int	keyword_current_count = 0;
			if(dictionary.containsKey(key.toString()))
				keyword_current_count = dictionary.get(key.toString());
			
			
			for(TextArrayWritable textA : values){

				// 计算词全局频率
				keyword_total_count += 1;
				keyword_current_count +=1;
				
				String[] clos = textA.toStrings();
				
				
				//准备计算idf的数据
				String art_rowkey = (String)clos[3];
				String key_standlone = art_rowkey+"|"+key.toString();
				int key_art_count = 0 ;
				if(idf_count.containsKey(key_standlone))
					key_art_count = idf_count.get(key.toString());
				
				key_art_count+=1;
				idf_count.put(key_standlone, key_art_count);
				

			}
			
			dictionary.put(key.toString(), keyword_current_count);
		}
		
		@Override
		 protected void cleanup(Context context){
			
		
		}
	
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);

			   String[] fields = {i_CONTENT,i_SUBTITLE,i_TITLE};
			   conf.setStrings("index.fields", fields);
			   Job job = Job.getInstance(conf);

			   Scan scan = new Scan();
//			   scan.setFilter(filter1);

			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
			           Text.class,         
			           ArrayWritable.class,  
			           job);     
			   Date date = new Date();
			   job.setJobName("FunctionsKeyWods_"+date);
			   job.setJarByClass(FunctionsKeyWordsMR.class);
			   job.setReducerClass(Reducer.class);
			   job.setMapOutputKeyClass(Text.class);
			   job.setMapOutputValueClass(TextArrayWritable.class);
			   job.setOutputFormatClass(NullOutputFormat.class);
			   TableMapReduceUtil.initTableReducerJob(TABLENAME, Reducer.class, job);
//			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			

}
