package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.hbase.mapreduce.TableReducer;
import org.apache.hadoop.io.ArrayWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import hbaseextends.TextArrayWritable;

public class HbaseArtSim {
	
	public static final String TABLENAME="GDFinancialPDFSim";
	public static final String iCFAMILY="a";
	public static final String i_CONTENT = "content";
	public static final String i_TITLE = "title";
	public static final String i_FILENAME = "filename";
	public static final int SIMLEN = 8;
	
	public static class Mapper extends  TableMapper<Text, Text> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		
		@Override
		protected void setup(Context context){
			

		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			
			String data_row_key = new String(value.getRow(),"utf8");
		 	
//			String i_content =new String(value.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes()));
//			 
//			String i_title =new String(value.getValue(iCFAMILY.getBytes(), i_TITLE.getBytes()));
		 
		 	
//			String filename =new String(value.getValue(iCFAMILY.getBytes(), i_FILENAME.getBytes()));

			String filename = null;
			List<Cell> cr =value.getColumnCells(iCFAMILY.getBytes(), i_FILENAME.getBytes());
			for(Cell c :cr){
				String cv = new String(c.getValueArray(),c.getValueOffset(),c.getValueLength(),"utf8");
				if(! cv.trim().toLowerCase().equals("null")){
					filename = cv;
				}
				break;
			}		  
		 	
		 	try {

//			 	String source =  "{"+
//							"\"title\":\""+i_title+"\"," +
//							"\"filename\":\""+filename+"\"," +
//							"\"uuid\":\""+data_row_key+"\","+
//							"\"content\":\""+i_content+"\""+
//							"}";
//			 	System.out.println(source);
	 		    Text filetxt = new Text(filename);
	 		    System.out.println(data_row_key.substring(0,SIMLEN));
			 	context.write(new Text(data_row_key.substring(0,SIMLEN)), filetxt);
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
	 
	}
		
  
public static class cReducer extends Reducer<Text,Text,NullWritable,NullWritable>{
	    public static Logger LOG = LoggerFactory.getLogger(Reducer.class);
		
		@Override
		protected void setup(Context context){
			
		}
		
		@Override
		protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
			
			List<String> flist = new ArrayList<String>();		
			for(Text textA : values){
				flist.add(textA.toString());
			}	
			
			if(flist.size() > 1 ){
				System.out.println("----");
				for(String s : flist){
					LOG.info(s);
				}
				LOG.info("!----");
			}
			context.write(NullWritable.get(),NullWritable.get());
		}
		 
		@Override
		 protected void cleanup(Context context){

		}
	
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);

			   String[] fields = {i_CONTENT,i_FILENAME,i_TITLE};
			   conf.setStrings("index.fields", fields);
			   Job job = Job.getInstance(conf);

			   Scan scan = new Scan();
//			   scan.setFilter(filter1);

			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			     
			   Date date = new Date();
			   job.setJobName("artsim1_"+date);
			   job.setJarByClass(HbaseArtSim.class);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
			           Text.class,         
			           ArrayWritable.class,  
			           job);   
//			   TableMapReduceUtil.initTableReducerJob(TABLENAME, Reducer.class, job);
			   job.setReducerClass(cReducer.class);
			   job.setMapOutputKeyClass(Text.class);
			   job.setMapOutputValueClass(Text.class);
			   job.setOutputFormatClass(NullOutputFormat.class);
			  
//			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			
			

}
