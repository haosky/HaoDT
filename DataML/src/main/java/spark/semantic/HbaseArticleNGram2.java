package spark.semantic;

import org.apache.spark.SparkContext;
import org.apache.spark.rdd.NewHadoopRDD;
import org.apache.spark.sql.SparkSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.spark.api.java.JavaNewHadoopRDD;
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
import org.apache.hadoop.io.NullWritable;
import org.apache.spark.sql.Dataset;
import scala.reflect.ClassTag$;
import org.apache.hadoop.hbase.util.Base64;
import org.apache.spark.api.java.function.FlatMapFunction;
import org.apache.spark.api.java.function.Function;
import org.apache.spark.storage.StorageLevel;
import scala.runtime.AbstractFunction1;
import java.io.Serializable;
import java.util.Iterator;
import java.util.List;
import org.apache.hadoop.hbase.protobuf.ProtobufUtil;  
import org.apache.hadoop.hbase.protobuf.generated.ClientProtos;  
import org.apache.spark.ml.feature.NGram;
import java.util.ArrayList;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.Metadata;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.types.*;
import java.util.Date;


public class HbaseArticleNGram2 {
	 public static Logger LOG = LoggerFactory.getLogger(HbaseArticleNGram2.class);
	 public static final String TABLENAME="GuangDongFinancialPDF";
	 public static final String iCFAMILY="a";
	 public static final String i_CONTENT = "content";
	 
	 static String convertScanToString(Scan scan) throws IOException {
		 	ClientProtos.Scan proto = ProtobufUtil.toScan(scan);  
	        String ScanToString = Base64.encodeBytes(proto.toByteArray());  	        
	        return ScanToString;
	    }

	
	 static abstract class SerializableFunction1<T1,R>
     extends AbstractFunction1<T1,R> implements Serializable {}
	
	@SuppressWarnings("unchecked")
	public static void main(String args[]) throws IOException{
		SparkSession spark = SparkSession
			      .builder()
			      .appName("Ng")
			      .getOrCreate();
		System.out.println("Ng");

		Configuration conf = HBaseConfiguration.create();	
	    String[] fields = {"content"};

//	    Job job = Job.getInstance(conf);
	    
	    conf.set("hbase.zookeeper.quorum","192.168.18.236");
		conf.set("hbase.zookeeper.property.clientPort", "2181");
		conf.set("hbase.master", "gx.master");
	    conf.set("index.tablename", TABLENAME);
	    conf.set("index.familyname", iCFAMILY);
	    Scan scan = new Scan();
	    //	   scan.setFilter(filter1);
	    scan.addFamily("a".getBytes());
	    scan.addColumn("a".getBytes(),"content".getBytes());
	    scan.setCaching(256);
	    scan.setCacheBlocks(false);
	    scan.setMaxResultSize(2);
	    conf.set(TableInputFormat.INPUT_TABLE,  TABLENAME);
        conf.set(TableInputFormat.SCAN, TableMapReduceUtil.convertScanToString(scan));
        
		SparkContext sc = spark.sparkContext();
		sc.conf().set("spark.kryoserializer.buffer","4096");
		NewHadoopRDD<ImmutableBytesWritable,Result> hr = new NewHadoopRDD<ImmutableBytesWritable,Result>(sc, TableInputFormat.class, ImmutableBytesWritable.class, Result.class, conf);
		
			    
		ClassTag<ImmutableBytesWritable> keyob =  ClassTag$.MODULE$.apply(ImmutableBytesWritable.class);
		
		ClassTag<Result> valueob =  ClassTag$.MODULE$.apply(Result.class);
		
		JavaNewHadoopRDD<ImmutableBytesWritable, Result> jh = new JavaNewHadoopRDD<ImmutableBytesWritable, Result>(hr, keyob, valueob);
		 
		jh.persist(StorageLevel.MEMORY_AND_DISK());
			
		ClassTag<Row> text =  ClassTag$.MODULE$.apply(Row.class);
		
		
		JavaRDD<Row> jmapRDD = jh.map(new Function<Tuple2<ImmutableBytesWritable, Result>, Row>(){
			private final Logger log2 =  LoggerFactory.getLogger(SerializableFunction1.class);
			@Override
			public Row call(Tuple2<ImmutableBytesWritable, Result> t) throws Exception {
				// TODO Auto-generated method stub
				try{
					ByteArrayInputStream content_stream =new ByteArrayInputStream(t._2.getValue(iCFAMILY.getBytes(), i_CONTENT.getBytes()));
					String i_content =(String) BeanUtils.BytesToObject(content_stream);
					i_content = i_content.replace(" ", "");
//					return i_content.toCharArray();
					String data_row_key = new String(t._2.getRow(),"utf8");
					char[] chars = i_content.toCharArray();
					List<String> liststr = new ArrayList<String>();
					for(char c :chars){
						liststr.add(String.valueOf(c));
					}
					Date d = new Date();
					return RowFactory.create(Integer.parseInt(d.getTime() - 1492682473000l+""),liststr);
					}catch(Exception e){
						log2.error(e.getMessage());
						return null;
				}
			}
			
		});		
		List<Row> listchar = jmapRDD.collect();
		LOG.info("-------------------------scan row "+listchar.size());
				
		StructType schema = new StructType(new StructField[]{
			      new StructField("id", DataTypes.IntegerType, false, Metadata.empty()),
			      new StructField(
			        "words", DataTypes.createArrayType(DataTypes.StringType), false, Metadata.empty())
			    });
		
		Dataset<Row> documentDF = spark.createDataFrame(listchar, schema);
		NGram ngramTransformer = new NGram().setN(2).setInputCol("words").setOutputCol("ngrams");

	    Dataset<Row> ngramDataFrame = ngramTransformer.transform(documentDF);
	    ngramDataFrame.select("ngrams").show(false);
	    ngramDataFrame.javaRDD().saveAsObjectFile("/spark/ngramdataPDFOBJ");

		spark.stop();
		
	}
 
	
}
 
