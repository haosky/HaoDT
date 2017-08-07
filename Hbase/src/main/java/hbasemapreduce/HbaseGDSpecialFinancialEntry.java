package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
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
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hankcs.hanlp.seg.common.Term;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.List;
import java.util.ArrayList;
import java.util.HashSet;
import customcommon.JsonUtils;
import hbaseutils.HbaseDao;
import customcommon.StrUtils;
public class HbaseGDSpecialFinancialEntry {
	
	public static final String TABLENAME="GDSpecialFinancial";
	public static final String OutTABLENAME="GDSpecialFinancial";
	public static final String iCFAMILY="a";
 	
	public static final String i_PROJECT = "project";
	public static final String i_FINICAL_UNIT = "finical_unit";
	public static final String i_FINICAL_NAME = "finical_name";
	public static final String i_DATE = "date";
	public static final String i_DOC = "doc";
	public static final String i_CONTENT = "content";
	public static final String i_UNIT = "unit";
	public static final String i_FINICAL ="finical"; 
	public static final String i_FL_TYPE = "fl_type"; 
	public static final String i_UUID = "uuid"; 
	public static final String i_SUBMITER = "submiter"; 
	public static final String i_ENTRIES = "entries"; 
	
	
	public static final int SIMLEN = 8;
	
	public static class Mapper extends  TableMapper<Text, Text> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		
		@Override
		protected void setup(Context context){
			

		}
		
		@Override
		protected void map(ImmutableBytesWritable row, Result value, Context context) throws IOException, InterruptedException{ 
			
			String data_row_key = Bytes.toString(value.getRow());
		 		 		 	
		 	try {
		 		String PROJECT = getCellData(value,i_PROJECT);
				String CONTENT = getCellData(value,i_CONTENT);
				
				List<Term> kwitems = StrUtils.hanlpToken(CONTENT);
				HashSet<String> kwset = new HashSet<String>();
//				hm.put(i_CONTENT,CONTENT);
				for(Term st:kwitems){
//					System.out.println(st.word+" "+st.nature);
					if(st.nature.equals("nt") || st.nature.equals("nr"))
					{
						kwset.add(st.word);
					}
				}
				ArrayList<String> lskw = new ArrayList<String>();
				for(String skw : kwset){
					lskw.add(skw);
				}
				String jsstr = JsonUtils.ListToJson(lskw);
				Text jsondata = new Text(jsstr);
	 		    context.write(new Text(data_row_key) , jsondata);
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
				p.addColumn("a".getBytes(), i_ENTRIES.getBytes(),bs);
				context.write(new ImmutableBytesWritable(bs), p);
			}catch(Exception e){
				
			}
		}
		 
		@Override
		 protected void cleanup(Context context){

		}
	
	}
	
	private static String getCellData(Result value,String column) throws UnsupportedEncodingException{
		
		return HbaseDao.getCellData(value, column, iCFAMILY);
		
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
		conf.set("index.tablename", TABLENAME);
		   conf.set("index.familyname", iCFAMILY);

			   String[] fields = {i_CONTENT};
			   conf.setStrings("index.fields", fields);
			   Job job = Job.getInstance(conf);
			   job.setJobName("HbaseGDSpecialFinancialEntry");
			   Scan scan = new Scan();
//			   scan.setRowPrefixFilter("10003899".getBytes());
//			   scan.setFilter(filter1);

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
			
}
