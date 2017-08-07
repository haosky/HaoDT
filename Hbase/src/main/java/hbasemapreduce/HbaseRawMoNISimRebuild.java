package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop .io.NullWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.gx.intell.Query.ContentSimQuery;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.List;
import java.util.Random;

import hbaseutils.HbaseDao;

public class HbaseRawMoNISimRebuild {
	
	public static final String TABLENAME="CaiZhengMoNiSim";
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
	
	public static class Mapper extends  TableMapper<NullWritable, NullWritable> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		public HbaseDao hdao = null;
		@Override
		protected void setup(Context context){
			
			hdao = new HbaseDao();	
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
				
				String id = data_row_key.substring(20);
	     		ContentSimQuery cq = new ContentSimQuery();
	     		String simhash = cq.getConentSimHash(CONTENT);
	     		
	     		cq.destory();
				Put p = new Put((simhash+id).getBytes());
				Random r = new Random();
				int finical =(int)(r.nextDouble() * 10000);
				p.addColumn("a".getBytes(), "project".getBytes(), PROJECT.getBytes());
				p.addColumn("a".getBytes(), "finical_unit".getBytes(), FINICAL_UNIT.getBytes());
				p.addColumn("a".getBytes(), "finical_name".getBytes(), FINICAL_NAME.getBytes());
				p.addColumn("a".getBytes(), "date".getBytes(), DATE.getBytes());
				p.addColumn("a".getBytes(), "doc".getBytes(), DOC.getBytes());
				p.addColumn("a".getBytes(), "content".getBytes(), CONTENT.getBytes());
				p.addColumn("a".getBytes(), "unit".getBytes(), UNIT.getBytes());
				p.addColumn("a".getBytes(), "finical".getBytes(), FINICAL.getBytes()); 
				p.addColumn("a".getBytes(), "simhash".getBytes(),simhash.getBytes()); 
				p.addColumn("a".getBytes(), "fl_type".getBytes(),FL_TYPE.getBytes()); 
				p.addColumn("a".getBytes(), "bbdw".getBytes(),BBDW.getBytes()); 
				
				hdao.put("CaiZhengMoNiSim2", p);

		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
		@Override
		protected void cleanup(Context context){
			
			hdao.destory();
		}
	 
	}
		
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);
		   
			   Job job = Job.getInstance(conf);
			   job.setJobName("RawMoNiSimRebuild");
			   Scan scan = new Scan();
//			   scan.setRowPrefixFilter("10003899".getBytes());
//			   scan.setFilter(filter1);

			   scan.setCaching(256);
			   scan.setCacheBlocks(false);
			   
			   job.setJarByClass(HbaseRawMoNISimRebuild.class);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
					   NullWritable.class,         
					   NullWritable.class,  
			           job);   
//			   TableMapReduceUtil.initTableReducerJob(TABLENAME, Reducer.class, job);
			   job.setOutputFormatClass(NullOutputFormat.class);
			   job.setNumReduceTasks(0);
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
