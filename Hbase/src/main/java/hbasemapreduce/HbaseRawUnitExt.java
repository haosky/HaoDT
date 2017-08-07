package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Mutation;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.hbase.mapreduce.TableReducer;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop .io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.List;

import hbaseutils.HbaseDao;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;

public class HbaseRawUnitExt {
	
	public static final String TABLENAME="CaiZhengMoNiSim";
	public static final String OutTABLENAME="Raw_Organial";
	public static final String iCFAMILY="a";
	public static final String i_FL_TYPE = "bbdw"; 
	
	public static class Mapper extends  TableMapper<Text, Text> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		@Override
		protected void setup(Context context){
			

		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
				 		 	
		 	try {
				String FL_TYPE = getCellData(value,i_FL_TYPE); 
				if(FL_TYPE.equals("\\N"))
						return;
	 		    context.write(new Text(FL_TYPE), new Text(FL_TYPE));
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
	 
	}
		
  
public static class cReducer extends TableReducer<Text,Text,ImmutableBytesWritable>{
	    public static Logger LOG = LoggerFactory.getLogger(cReducer.class);
		
		@Override
		protected void setup(Context context){
			
		}
		
		@Override
		protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
			 
			try{
				byte[] bs = Bytes.toBytes(key.toString());
				Put p = new Put(bs);
				p.addColumn("a".getBytes(), i_FL_TYPE.getBytes(),bs);
				context.write(new ImmutableBytesWritable(bs), p);
			}catch(Exception e){
				
			}
		}
		 
		@Override
		 protected void cleanup(Context context){

		}
	
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);

			   String[] fields = {i_FL_TYPE};
			   conf.setStrings("index.fields", fields);
			   Job job = Job.getInstance(conf);
			   job.setJobName("hunit");
			   Scan scan = new Scan();
			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			   
			   job.setJarByClass(HbaseRawUnitExt.class);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
			           Text.class,         
			           Text.class,  
			           job);   
		 
			   job.setMapOutputKeyClass(Text.class);
			   job.setMapOutputValueClass(Text.class);
			   job.setOutputKeyClass(ImmutableBytesWritable.class);
			   job.setOutputValueClass(Mutation.class);
			   job.setOutputFormatClass(NullOutputFormat.class);
			   TableMapReduceUtil.initTableReducerJob(OutTABLENAME, cReducer.class, job);
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
