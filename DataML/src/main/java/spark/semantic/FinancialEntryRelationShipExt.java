package spark.semantic;

import java.io.IOException;
import java.io.Serializable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.filter.Filter;
import org.apache.hadoop.hbase.filter.PageFilter;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableInputFormat;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.protobuf.ProtobufUtil;
import org.apache.hadoop.hbase.protobuf.generated.ClientProtos;
import org.apache.hadoop.hbase.util.Base64;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.spark.SparkContext;
import org.apache.spark.api.java.JavaNewHadoopRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.function.PairFunction;
import org.apache.spark.rdd.NewHadoopRDD;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.storage.StorageLevel;
import neo4jclient.NeoDriver;
import com.hankcs.hanlp.seg.common.Term;
import java.util.List;
import java.util.ArrayList;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import hbaseutils.HbaseDao;
import customcommon.StrUtils;
import scala.Tuple2;
import scala.reflect.ClassTag;
import scala.reflect.ClassTag$;
import scala.runtime.AbstractFunction1;
import static org.neo4j.driver.v1.Values.parameters;

public class FinancialEntryRelationShipExt {
	public static Logger LOG = LoggerFactory.getLogger(FinancialEntryRelationShipExt.class);
	 public static final String TABLENAME="GDSpecialFinancial";
	 public static final String iCFAMILY="a";
	 public static final String i_CONTENT = "content";
	 public static final String i_PROJECT = "project";
	 public static final String i_ENTRY = "entry";

	 
	 static String convertScanToString(Scan scan) throws IOException {
		 	ClientProtos.Scan proto = ProtobufUtil.toScan(scan);  
	        String ScanToString = Base64.encodeBytes(proto.toByteArray());  	        
	        return ScanToString;
	    }

	
	 static abstract class SerializableFunction1<T1,R>
     extends AbstractFunction1<T1,R> implements Serializable {

		/**
		 * 
		 */
		private static final long serialVersionUID = 1L;}
	
	@SuppressWarnings("unchecked")
	public static void main(String args[]) throws IOException{
		SparkSession spark = SparkSession
			      .builder()
			      .appName("FinancialEntryRelationShipExt2")
			      .getOrCreate();
		
		Configuration conf = HBaseConfiguration.create();	
	    String[] fields = {"content","project"};

	    conf.set("hbase.zookeeper.quorum","192.168.1.122");
		conf.set("hbase.zookeeper.property.clientPort", "2181");
		conf.set("hbase.master", "192.168.1.122");
	    conf.set("index.tablename", TABLENAME);
	    conf.set("index.familyname", iCFAMILY);
	    Scan scan = new Scan();
	    // 扫描 10000 行
//	    Filter filter = new PageFilter(2);
//	    scan.setFilter(filter);
	    scan.addFamily(iCFAMILY.getBytes());
	    scan.addColumn(iCFAMILY.getBytes(),"content".getBytes()).addColumn(iCFAMILY.getBytes(),i_PROJECT.getBytes());
//	    scan.setCaching(256);
	    scan.setCacheBlocks(false);
	    conf.set(TableInputFormat.INPUT_TABLE, TABLENAME);
        conf.set(TableInputFormat.SCAN, TableMapReduceUtil.convertScanToString(scan));
       
		SparkContext sc = spark.sparkContext();
		NewHadoopRDD<ImmutableBytesWritable,Result> hr = new NewHadoopRDD<ImmutableBytesWritable,Result>(sc, TableInputFormat.class, ImmutableBytesWritable.class, Result.class, conf);
		
ClassTag<ImmutableBytesWritable> keyob =  ClassTag$.MODULE$.apply(ImmutableBytesWritable.class);
		
		ClassTag<Result> valueob =  ClassTag$.MODULE$.apply(Result.class);
		
		JavaNewHadoopRDD<ImmutableBytesWritable, Result> jh = new JavaNewHadoopRDD<ImmutableBytesWritable, Result>(hr, keyob, valueob);
		 
		jh.persist(StorageLevel.MEMORY_AND_DISK());
		
	
		ClassTag<NullWritable> nw =  ClassTag$.MODULE$.apply(NullWritable.class);
		
		ClassTag<Text> text =  ClassTag$.MODULE$.apply(Text.class);

		HPFz<Tuple2<ImmutableBytesWritable, Result>,String,List> pf = new HPFz<Tuple2<ImmutableBytesWritable, Result>,String,List>(){
			private final Logger log2 =  LoggerFactory.getLogger(HPFz.class);
			
			@Override
			public Tuple2<String,List> call(Tuple2<ImmutableBytesWritable, Result> t) throws Exception {
				
				// TODO Auto-generated method stub
				List<String> vocabulary = new ArrayList<String>();
				try{
				NeoDriver nd = new NeoDriver();
			    HbaseDao hd = new HbaseDao();
				String rk = Bytes.toString(t._2.getRow());
				String i_content =Bytes.toString((t._2.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes())));
				String i_project =Bytes.toString((t._2.getValue(iCFAMILY.getBytes(), i_PROJECT.getBytes())));

		
				List<Term> kws = StrUtils.hanlpToken(i_content);
				nd.createSession();
				for(Term kw : kws){
					String stype = kw.nature.toString();
					if( stype.equals("nt") || stype.equals("nr")){
						vocabulary.add(kw.word.toString()+"/"+kw.nature);
					}
				}
				if(i_project == null || vocabulary.size() == 0){
					return new Tuple2<String,List>("", vocabulary);
				}

				nd.runPutStatement("MERGE (a:SpecialFinancialProject {project:{project},uuid:{uuid}}) ON CREATE SET a.project = {project}",
		                  parameters("project",i_project,"uuid",rk) );
				
				for(String kw : vocabulary){
					String[] skwsplit = kw.split("/");
				
					nd.runPutStatement("MERGE (b:SpecialFinancialEntry {entry: {entry},type:{type}}) ON CREATE SET b.entry = {entry}",
			                  parameters("entry",skwsplit[0],"type",skwsplit[1]) );
						
					nd.runPutStatement("MATCH (c:SpecialFinancialEntry {entry: {entry}}) "
							+ "MATCH (d:SpecialFinancialProject {project: {project}}) "
							+ "MERGE (c)-[r:InProject] -> (d) "
							+ "ON CREATE SET  r.project = {project} "
							+ "ON MATCH SET  r.project = {project}",
			                  parameters("project",i_project,"entry",skwsplit[0]) );			
				}
				nd.destoryDriver();
				if(vocabulary.size() > 0){
					Put ps = new Put(t._2.getRow());
					ps.addColumn(iCFAMILY.getBytes(), i_ENTRY.getBytes(), vocabulary.toString().getBytes());
					hd.put(TABLENAME, ps);
				}
				return new Tuple2<String,List>(rk, vocabulary);
				
				}catch(Exception e){
					LOG.error(e.getMessage());
					System.err.println(e.getMessage());
				}
				return new Tuple2<String,List>("", vocabulary);
			}
			 
		 };
		 
		  
		 JavaPairRDD<String,List> p = jh.mapToPair(pf);
//		 NeoDriver nd = new NeoDriver();
//	     nd.createSession();
//	     	
//	     HbaseDao hd = new HbaseDao();
		 List<Tuple2<String,List>> it = p.collect();
//		 LOG.info("===================="+it.size()+"====================");
//		 List<String> kwexists = new ArrayList<String>();
//		 String liast = null;
//		 for(Tuple2<String,List> un :it)
//		 {	
//
//		}
//			 
	
		 LOG.info("<<<<<<<<<<<<<<<<<<<<liast>>>>>>>>>>>>>>>>.");
		 LOG.info("=================get JavaPairRDD values line 182======================"); 
	}
	
}

abstract class HPFz<T,K,V> implements PairFunction<T,K,V>{}
