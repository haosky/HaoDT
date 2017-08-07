package hbasemapreduce;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop .io.Text;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.mapreduce.Job;
import java.lang.Math;
import org.elasticsearch.hadoop.mr.EsOutputFormat;
import org.junit.Test;
import org.slf4j.Logger;
import java.util.Random;
import org.slf4j.LoggerFactory;
import java.util.Date;

import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.seg.Segment;
import com.hankcs.hanlp.seg.common.Term;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import customcommon.JsonUtils;
import hbaseutils.HbaseDao;

public class HbaseGDSpecialFinancial2Es {
	
	public static final String TABLENAME="GDSpecialFinancial";
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
	public static final String i_ENTRY = "entry";
	
	public static final String o_StmtSentence = "StmtSentence";
	public static final String o_KwEntry = "KwEntry";
	public static final String o_OrgEntry = "OrgEntry";
	public static final String o_PleceEntry = "PleceEntry";
	public static final String o_YyEntry = "YyEntry";
	public static final String o_ChineseEntry = "ChineseEntry";
	public static final String o_UPLOAD_AT = "upload_at"; 
	
	
	public static final int SIMLEN = 8;
	
	public static class Mapper extends  TableMapper<NullWritable, Text> {
		public static Logger LOG = LoggerFactory.getLogger(Mapper.class);
		private Segment segment = null;
		private Segment segment1 = null;
		private Segment segment2 = null;
		private Segment segment3 =null;
		
		@Override
		protected void setup(Context context){
			  segment = HanLP.newSegment().enableNameRecognize(true);
			  segment1 = HanLP.newSegment().enableTranslatedNameRecognize(true);
			  segment2 = HanLP.newSegment().enablePlaceRecognize(true);
			  segment3 = HanLP.newSegment().enableOrganizationRecognize(true);
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
				String FL_TYPE = getCellData(value,i_FL_TYPE); 
				String UUID = getCellData(value,i_UUID); 
				String SUBMITER = getCellData(value,i_SUBMITER); 
				String ENTRY = null;
				
				try{
					ENTRY = new String(getCellData(value,i_ENTRY)); 
				}catch(Exception e){
					
				}
				HashMap hm = new HashMap();
				hm.put(i_PROJECT, PROJECT);
				hm.put(i_FINICAL_UNIT,FINICAL_UNIT);
				hm.put(i_FINICAL_NAME,FINICAL_NAME);
				hm.put(i_DATE,DATE);
				hm.put(i_DOC,DOC);
				hm.put(i_CONTENT,CONTENT);
				hm.put(i_UNIT,UNIT);
				hm.put(i_FINICAL,FINICAL);
				hm.put(i_FL_TYPE,FL_TYPE);
				hm.put(i_UUID,UUID);
				hm.put(i_SUBMITER,SUBMITER);
				hm.put("_uuid",data_row_key);
				if(ENTRY !=null && ! ENTRY.equals("")){
					hm.put(i_ENTRY,ENTRY);
					hm.put("isre",true);
				}
				String CONTENT2 = CONTENT.substring(0, Math.min(0,1200));
				
				// 中国人民
				
				List<String> listChineseEntry = new ArrayList<String>();
				List<Term> termList = segment.seg(CONTENT);
				for(Term t:termList){
					if(t.nature.toString().equals("nr"))
					listChineseEntry.add(t.word.toString());
				}
				 
				// 义音
				
				List<String> listYyEntry = new ArrayList<String>();
				List<Term> yytermList = segment1.seg(CONTENT);
				for(Term t1:yytermList){
					if(t1.nature.toString().equals("nr"))
						listYyEntry.add(t1.word.toString());
				}
				
				// 地方
				
				List<String> listPleceEntry = new ArrayList<String>();
				List<Term> PlecetermList = segment2.seg(CONTENT);
				for(Term t2:PlecetermList){
					if(t2.nature.toString().equals("nr"))
						listPleceEntry.add(t2.word.toString());
				}
				
	 		   // 机构
				
				List<String> listOrgEntry = new ArrayList<String>();
				List<Term> OrgtermList = segment3.seg(CONTENT);
				for(Term t3:OrgtermList){
					if(t3.nature.toString().equals("nt"))
						listOrgEntry.add(t3.word.toString());
				}
				
				
			   List<String> keywordList = HanLP.extractKeyword(CONTENT, 8);
			   List<String> sentenceList = HanLP.extractSummary(CONTENT2, 3);
			   
			   hm.put(o_StmtSentence,JsonUtils.ListToJson(sentenceList));
			   hm.put(o_KwEntry,JsonUtils.ListToJson(keywordList));
			   hm.put(o_OrgEntry,JsonUtils.ListToJson(listOrgEntry));
			   hm.put(o_PleceEntry,JsonUtils.ListToJson(listPleceEntry));
			   hm.put(o_YyEntry,JsonUtils.ListToJson(listYyEntry));
			   hm.put(o_ChineseEntry,JsonUtils.ListToJson(listChineseEntry));
	
			   Date date = new Date();
			   long l = date.getTime();
			   long lx = (long)(new Random().nextInt(300)*72000000);
			   Date d2 = new Date(l - lx);
			   String upload_at_c = dateToString(d2);
			   hm.put(o_UPLOAD_AT,upload_at_c);
			   String jsstr = JsonUtils.mapToJSON(hm);
			   Text jsondata = new Text(jsstr);
			   context.write(NullWritable.get(), jsondata);
	 		    
		 	} catch (IOException e) {
				// TODO Auto-generated catch block
				System.err.print(e.getMessage());
				
			}
		 			  	
		}
	 
	}
		 
	private static String getCellData(Result value,String column) throws UnsupportedEncodingException{
		
		return HbaseDao.getCellData(value, column, iCFAMILY);
		
	}
	
	public static Job configureJob(Configuration conf, String [] args)
			 throws IOException {
			
			   conf.set("index.tablename", TABLENAME);
			   conf.set("index.familyname", iCFAMILY);
			   conf.set("es.nodes", "haosky-UN65U"); 
			   conf.set("zookeeper.session.timeout", "9000000");
			   conf.set("es.port", "9200"); 
			   conf.set("es.index.auto.create", "yes");
			   conf.set("es.resource", "gdspecial_v2/financial");
			   conf.set("es.input.json", "yes"); 
			   conf.set("es.mapping.id", "_uuid");			   
			   Job job = Job.getInstance(conf);
			   job.setJobName("GDSpecialFinancial");
			   Scan scan = new Scan();
//			   scan.setRowPrefixFilter("10003899".getBytes());
//			   scan.setFilter(filter1);

//			   scan.setCaching(1024);
			   scan.setCacheBlocks(false);
			   
			   job.setJarByClass(HbaseGDSpecialFinancial2Es.class);
			   TableMapReduceUtil.initTableMapperJob(
					   TABLENAME,    
					   scan,
					   Mapper.class,    
					   NullWritable.class,         
			           Text.class,
			           job);   
//			   TableMapReduceUtil.initTableReducerJob(TABLENAME, Reducer.class, job);
			   job.setMapOutputValueClass(Text.class); 
			   job.setOutputFormatClass(EsOutputFormat.class);
			  
			   job.setNumReduceTasks(0);
			   return job;
			 }
			 public static void main(String[] args) throws Exception {
			   
			   Configuration conf = HBaseConfiguration.create();
			   Job job = configureJob(conf,args);
			   System.exit(job.waitForCompletion(true) ? 0 : 1);
			 }
			 
		 public static String dateToString(Date time){ 
			    SimpleDateFormat formatter; 
			    formatter = new SimpleDateFormat ("yyyy/MM/dd HH:mm:ss"); 
			    String ctime = formatter.format(time); 

			    return ctime; 
		} 


			
}
