package spark.semantic;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.Serializable;
import java.util.Set;

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
import org.apache.spark.ml.linalg.Matrices;
import org.apache.spark.ml.linalg.Matrix;
import org.apache.spark.ml.linalg.DenseMatrix;
import java.util.List;
import java.util.HashSet;
import java.util.HashMap;
import java.util.ArrayList;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import customcommon.StrUtils;
import scala.Tuple2;
import scala.reflect.ClassTag;
import scala.reflect.ClassTag$;
import scala.runtime.AbstractFunction1;

public class RawSuggestNBayes {
	public static Logger LOG = LoggerFactory.getLogger(RawSuggestNBayes.class);
	 public static final String TABLENAME="CaiZhengMoNiSim";
	 public static final String iCFAMILY="a";
	 public static final String i_CONTENT = "content";
	 public static final String i_BBDW = "bbdw";

	 
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
			      .appName("RawSuggestNBayes")
			      .getOrCreate();
		
		Configuration conf = HBaseConfiguration.create();	
	    String[] fields = {"content","bbdw"};

	    conf.set("hbase.zookeeper.quorum","192.168.1.122");
		conf.set("hbase.zookeeper.property.clientPort", "2181");
		conf.set("hbase.master", "192.168.1.122");
	    conf.set("index.tablename", TABLENAME);
	    conf.set("index.familyname", iCFAMILY);
	    Scan scan = new Scan();
	    // 扫描 10000 行
	    Filter filter = new PageFilter(5000);
	    scan.setFilter(filter);
	    scan.addFamily(iCFAMILY.getBytes());
	    scan.addColumn(iCFAMILY.getBytes(),"content".getBytes()).addColumn(iCFAMILY.getBytes(),"bbdw".getBytes());
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

		HPFS<Tuple2<ImmutableBytesWritable, Result>,String,List> pf = new HPFS<Tuple2<ImmutableBytesWritable, Result>,String,List>(){
			private final Logger log2 =  LoggerFactory.getLogger(HPFS.class);
			@Override
			public Tuple2<String, List> call(Tuple2<ImmutableBytesWritable, Result> t) throws Exception {
				// TODO Auto-generated method stub
				try{
				String i_content =Bytes.toString((t._2.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes())));
				
				String i_bbdw =Bytes.toString((t._2.getValue(iCFAMILY.getBytes(), i_BBDW.getBytes())));
		
				List<String> kws = StrUtils.jiebaToken(i_content);
				List<String> vocabulary = new ArrayList<String>();
				for(String kw : kws){
					vocabulary.add(kw);
				}
//	 		    Text tbbdw = new Text(i_bbdw);
	 		    // 机构 ， 词典
				return new Tuple2<String,List>(i_bbdw, vocabulary);
				}catch(Exception e){
					LOG.error(e.getMessage());
					System.err.println(e.getMessage());
				}
				return null;
			}
			 
		 };
		 
		  
		 JavaPairRDD<String,List> p = jh.mapToPair(pf);
		 
		 LOG.info("=================get JavaPairRDD values line 141======================");
		 JavaRDD<List> vocabullarySubSet =  p.values();
		 //构建词典
		 HashSet<String> gobalVocabulary = new HashSet<String>();
		 List<List> lvocabhashset = vocabullarySubSet.collect();
		 int doclen = lvocabhashset.size();
		 LOG.info("doc length == "+doclen);
		 HashMap<String,Integer> tf = new HashMap<String,Integer>();
		 HashMap<String,Integer> idf = new HashMap<String,Integer>();
	 
		 for(List<String> kwset:lvocabhashset){
			 // doc 
			 HashSet<String> dfkw = new HashSet<String>();
			 for(String kw:kwset){
				 // kw
				 if(! tf.containsKey(kw))
					 tf.put(kw, 0);
				 int kwcount = tf.get(kw);
				 tf.put(kw, kwcount+=1);
				 gobalVocabulary.add(kw);
				 if(dfkw.contains(kw))
					 continue;
				 dfkw.add(kw);
				 if(! idf.containsKey(kw))
					 idf.put(kw, 0);
				 idf.put(kw, kwcount+=1);
			 }
			 
		 }
		 
		 int vocablen = gobalVocabulary.size();
		 //构建机构	
		 JavaRDD<String> bbdwLabelsRDD =  p.keys();
		 List<String> bbdwLabels = bbdwLabelsRDD.collect();
		 HashMap<String,Integer> bbdwIndexMap = new HashMap<String,Integer>();
		 int labeli = 0;
		 for(String t:bbdwLabels)
		 {
			 bbdwIndexMap.put(t,labeli);
			 labeli +=1;
		 }
		 
		 int classTypelen = bbdwIndexMap.size();
		 
		 //建立索引
		 HashMap<String,Integer> vocabIndexMap = new HashMap<String,Integer>(); 
		 int kwi = 0;
		 for(String kw:tf.keySet()){
			 vocabIndexMap.put(kw,kwi);
			 kwi+=1;
		 }
		 LOG.info("=============== 192 ===============");
		 Matrix tfMatrix = Matrices.zeros(doclen, vocablen);
		 DenseMatrix idfMatrix = (DenseMatrix)Matrices.zeros(1, vocablen);
		 
		 for(int i=0 ;i<=vocablen;i++){
			 
			 
		 }
		 
		
//		 tfMatrix.multiply(idfMatrix.transpose());
		 LOG.info("=============== 194 ===============");
//		 for(int i=0;i<=doclen;i++){
//			 
//		 }		 
	}
	
}

abstract class HPFS<T,K,V> implements PairFunction<T,K,V>{}
