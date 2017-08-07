package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop .io.Text;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.Job;
import org.elasticsearch.hadoop.mr.EsOutputFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.List;
import customcommon.JsonUtils;
import hbaseutils.HbaseDao;

import java.util.ArrayList;
import java.util.HashMap;

public class HbaseRawMoNISim {
	
	public static final String TABLENAME="CaiZhengMoNiSim2";
	public static final String iCFAMILY="a";
 	
	public static final String i_PROJECT = "project";
	public static final String i_FINICAL_UNIT = "finical_unit";
	public static final String i_FINICAL_NAME = "finical_name";
	public static final String i_DATE = "date";
	public static final String i_DOC = "doc";
	public static final String i_CONTENT = "content";
	public static final String i_UNIT = "unit";
	public static final String i_FINICAL ="finical"; 
	public static final String i_SIMHASH = "simhash"; 
	public static final String i_FL_TYPE = "fl_type"; 
	public static final String i_BBDW = "bbdw"; 
	
	
	public static final int SIMLEN = 8;
	
	public static class Mapper extends  TableMapper<Text, Text> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		
		@Override
		protected void setup(Context context){
			

		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			
			String data_row_key = new String(value.getRow(),"utf8");
		 		 		 	
		 	try {
		 		String PROJECT = getCellData(value,i_PROJECT);
				String FINICAL_UNIT = getCellData(value,i_FINICAL_UNIT);
				String FINICAL_NAME = getCellData(value,i_FINICAL_NAME);
				String DATE = getCellData(value,i_DATE);
				String DOC = getCellData(value,i_DOC);
				String CONTENT = getCellData(value,i_CONTENT);
				String UNIT = getCellData(value,i_UNIT);
				String FINICAL = getCellData(value,i_FINICAL); 
				String SIMHASH = getCellData(value,i_SIMHASH); 
				String FL_TYPE = getCellData(value,i_FL_TYPE); 
				String BBDW = getCellData(value,i_BBDW); 
				
				HashMap hm = new HashMap();
				hm.put(i_PROJECT, PROJECT);
				hm.put(i_FINICAL_UNIT,FINICAL_UNIT);
				hm.put(i_FINICAL_NAME,FINICAL_NAME);
				hm.put(i_DATE,DATE);
				hm.put(i_DOC,DOC);
				hm.put(i_CONTENT,CONTENT);
				hm.put(i_UNIT,UNIT);
				hm.put(i_FINICAL,FINICAL);
				hm.put(i_SIMHASH,SIMHASH);
				hm.put(i_FL_TYPE,FL_TYPE);
				hm.put(i_BBDW,BBDW);
				hm.put("_uuid",data_row_key);
				
				String jsstr = JsonUtils.mapToJSON(hm);
				Text jsondata = new Text(jsstr);
	 		    context.write(new Text(data_row_key.substring(0,SIMLEN)), jsondata);
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
	 
	}
		
  
public static class cReducer extends Reducer<Text,Text,NullWritable,Text>{
	    public static Logger LOG = LoggerFactory.getLogger(Reducer.class);
		
		@Override
		protected void setup(Context context){
			
		}
		
		@Override
		protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
			
			List<Text> flist = new ArrayList<Text>();		
			for(Text textA : values){
				flist.add(textA);
			}	
			
			if(flist.size() > 1 ){
				for(Text s : flist){
//					System.out.println(s.toString());
					context.write(NullWritable.get(), s);
				}
			 
			}
			 
			flist.clear();
			
		}
		 
		@Override
		 protected void cleanup(Context context){

		}
	
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);

//			   String[] fields = {i_CONTENT,i_FILENAME,i_TITLE};
//			   conf.setStrings("index.fields", fields);
			   //			   scan.setFilter(filter1);
  
//			   String[] fields = {i_CONTENT,i_SUBTITLE,i_TITLE};
//			   conf.setStrings("index.fields", fields);
			   conf.set("es.nodes", "192.168.1.122");
			   conf.set("es.port", "9200"); 
			   conf.set("es.index.auto.create", "yes");
			   conf.set("es.resource", "monidatas/raw2");
			   conf.set("es.input.json", "yes"); 
			   conf.set("es.mapping.id", "_uuid");			   
			   Job job = Job.getInstance(conf);
			   job.setJobName("RawMoNiSim");
			   Scan scan = new Scan();
//			   scan.setRowPrefixFilter("10003899".getBytes());
//			   scan.setFilter(filter1);

			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			   
			   job.setJarByClass(HbaseRawMoNISim.class);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
			           Text.class,         
			           Text.class,  
			           job);   
//			   TableMapReduceUtil.initTableReducerJob(TABLENAME, Reducer.class, job);
			   job.setReducerClass(cReducer.class);
			   job.setMapOutputKeyClass(Text.class);
			   job.setMapOutputValueClass(Text.class);
			   job.setOutputKeyClass(NullWritable.class);
			   job.setOutputValueClass(Text.class);
			   job.setOutputFormatClass(EsOutputFormat.class);
			  
//			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			
			 private static String getCellData(Result value,String column) throws UnsupportedEncodingException{
					
					return HbaseDao.getCellData(value, column, iCFAMILY);
					
				}	

}
