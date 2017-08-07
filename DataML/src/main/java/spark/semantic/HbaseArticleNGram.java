package spark.semantic;

import org.apache.spark.SparkContext;
import org.apache.spark.rdd.NewHadoopRDD;
import org.apache.spark.rdd.RDD;
import org.apache.spark.sql.SparkSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.spark.api.java.JavaNewHadoopRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;

import customcommon.BeanUtils;
import scala.Tuple2;
import scala.reflect.ClassTag;

import java.io.ByteArrayInputStream;
import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableInputFormat;  
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableSplit;
import org.apache.hadoop.io.NullWritable;
import org.apache.spark.sql.Dataset;
import org.apache.hadoop.io.Text;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import scala.reflect.ClassTag$;
import org.apache.hadoop.hbase.util.Base64;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.spark.api.java.function.Function2;
import org.apache.spark.api.java.function.PairFunction;
import org.apache.spark.storage.StorageLevel;
import customcommon.StrUtils;
import hbasemapreduce.HbaseToEsMR;
import hbasesrc.HbaseSettings;
import scala.runtime.AbstractFunction1;
import java.io.Serializable;
import java.util.List;
import org.apache.hadoop.hbase.protobuf.ProtobufUtil;  
import org.apache.hadoop.hbase.protobuf.generated.ClientProtos;  
import org.apache.spark.ml.feature.NGram;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.Metadata;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import java.util.Set;

@SuppressWarnings("unused")
public class HbaseArticleNGram {
	public static Logger LOG = LoggerFactory.getLogger(HbaseArticleNGram.class);
	 public static final String TABLENAME="functions";
	 public static final String iCFAMILY="a";
	 public static final String i_CONTENT = "content";
	 public static final String i_SUBTITLE = "subTitle";
	 public static final String i_TITLE = "title";
	 
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
			      .appName("HadooRddExampefunctions")
			      .getOrCreate();
		
		Configuration conf = HBaseConfiguration.create();	
	    String[] fields = {"content","subTitle","title"};

//	    Job job = Job.getInstance(conf);
	    
	    conf.set("hbase.zookeeper.quorum","192.168.1.122");
		conf.set("hbase.zookeeper.property.clientPort", "2181");
		conf.set("hbase.master", "gx.master");
	    conf.set("index.tablename", TABLENAME);
	    conf.set("index.familyname", iCFAMILY);
	    Scan scan = new Scan();
	    //	   scan.setFilter(filter1);
	    scan.addFamily("a".getBytes());
	    scan.addColumn("a".getBytes(),"content".getBytes()).addColumn("a".getBytes(),"subTitle".getBytes()).addColumn("a".getBytes(),"title".getBytes());
//	    scan.setCaching(256);
	    scan.setCacheBlocks(false);
	    conf.set(TableInputFormat.INPUT_TABLE,  "functions");
        conf.set(TableInputFormat.SCAN, TableMapReduceUtil.convertScanToString(scan));
//        conf.set(TableInputFormat.SCAN_COLUMN_FAMILY, "a");
//        conf.setStrings(TableInputFormat.SCAN_COLUMNS,fields);
//        conf.set(TableInputFormat.SCAN_ROW_START,SCAN_ROW_START);
        
        
		SparkContext sc = spark.sparkContext();
		NewHadoopRDD<ImmutableBytesWritable,Result> hr = new NewHadoopRDD<ImmutableBytesWritable,Result>(sc, TableInputFormat.class, ImmutableBytesWritable.class, Result.class, conf);
		
//		 StructType schema = new StructType(new StructField[]{
//			      new StructField("label", DataTypes.DoubleType, false, Metadata.empty()),
//			      new StructField("sentence", DataTypes.StringType, false, Metadata.empty())
//			    });
//			    Dataset<Row> sentenceData = spark.createDataFrame(data, schema);
			    
		ClassTag<ImmutableBytesWritable> keyob =  ClassTag$.MODULE$.apply(ImmutableBytesWritable.class);
		
		ClassTag<Result> valueob =  ClassTag$.MODULE$.apply(Result.class);
		
		JavaNewHadoopRDD<ImmutableBytesWritable, Result> jh = new JavaNewHadoopRDD<ImmutableBytesWritable, Result>(hr, keyob, valueob);
		 
		jh.persist(StorageLevel.MEMORY_AND_DISK());
		
	
		ClassTag<NullWritable> nw =  ClassTag$.MODULE$.apply(NullWritable.class);
		
		ClassTag<Text> text =  ClassTag$.MODULE$.apply(Text.class);

		 LOG.info("109----------------------------------------------");
		 PFS<Tuple2<ImmutableBytesWritable, Result>,Text,Text> pf = new PFS<Tuple2<ImmutableBytesWritable, Result>,Text,Text>(){
			private final Logger log2 =  LoggerFactory.getLogger(PFS.class);
			@Override
			public Tuple2<Text, Text> call(Tuple2<ImmutableBytesWritable, Result> t) throws Exception {
				// TODO Auto-generated method stub
				try{
				String data_row_key = new String(t._2.getRow(),"utf8");
			 	
			 	ByteArrayInputStream content_stream =new ByteArrayInputStream(t._2.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes()));
				String i_content =(String) BeanUtils.BytesToObject(content_stream);
			 	
//				ByteArrayInputStream title_stream =new ByteArrayInputStream(t._2.getValue(iCFAMILY.getBytes(), i_TITLE.getBytes()));
//				String i_title =(String) BeanUtils.BytesToObject(title_stream);
//			 	
//				ByteArrayInputStream subtitle_stream =new ByteArrayInputStream(t._2.getValue(iCFAMILY.getBytes(), i_SUBTITLE.getBytes()));
//				String i_subTitle =(String) BeanUtils.BytesToObject(subtitle_stream);
//			 	
//			 	List<String> list_token = StrUtils.extractKeyWord(i_content,5);
//
//			 	String source =  "{"+
//						"\"title\":\""+i_title+"\"," +
//						"\"subTitle\":\""+i_subTitle+"\"," +
//						"\"uuid\":\""+data_row_key+"\","+
//						"\"content\":\""+i_content+"\""+
//						"}";
	 		    Text jsonDoc = new Text(i_content);
	 
				return new Tuple2<Text,Text>(new Text(data_row_key), jsonDoc);
				}catch(Exception e){
					LOG.error(e.getMessage());
					System.err.println(e.getMessage());
				}
				return null;
			}
			 
		 };
		 
		 JavaPairRDD<Text,Text> p = jh.mapToPair(pf);
		 
		 Set<Text> texts = p.collectAsMap().keySet();
		
		 
		 
		 StructType schema = new StructType(new StructField[]{
			      new StructField("id", DataTypes.StringType, false, Metadata.empty()),
			      new StructField(
			        "words",DataTypes.StringType, false, Metadata.empty())
			    });

//	    Dataset<Row> wordDataFrame = spark.createDataFrame(  , schema);
			    
//		 NGram ngramTransformer = new NGram().setN(2).setInputCol("words").setOutputCol("ngrams");	
		 
//		 JavaPairRDD<Text,Text> counts = p.reduceByKey(new Function2<Text,Text,Text>() {
//
//			@Override
//			public Text call(Text v1, Text v2) throws Exception {
//				// TODO Auto-generated method stub
//				return v2;
//			} 
//			 
//		}); 
//		counts.saveAsTextFile("/aa.txt");

		System.out.println("136 00----------------------------------------");
		spark.stop();
	}
	
}

abstract class  PFS<T,K,V> implements PairFunction<T,K,V>{}
