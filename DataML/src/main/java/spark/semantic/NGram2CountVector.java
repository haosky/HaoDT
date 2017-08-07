package spark.semantic;

import java.util.List;

import org.apache.spark.ml.feature.CountVectorizer;
import org.apache.spark.ml.feature.CountVectorizerModel;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import spark.semantic.HbaseArticleNGram2.SerializableFunction1;

import java.util.ArrayList;
import java.util.Arrays;

import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.function.Function;
import java.util.Random;

public class NGram2CountVector {
	public static Logger LOG = LoggerFactory.getLogger(NGram2CountVector.class);

	public static void main(String[] args) {
	    SparkSession spark = SparkSession
	      .builder()
	      .appName("ngramdataPDFCountVectorizerh")
	      .getOrCreate();

	    // $example on$
	    // Input data: Each row is a bag of words from a sentence or document.
	    JavaSparkContext sc = JavaSparkContext.fromSparkContext(spark.sparkContext());
	    JavaRDD<Row> ngramdata = sc.objectFile("/spark/ngramdataPDFOBJ");
	    
	 	JavaRDD<Row> clearngramdata = ngramdata.map(new Function<Row,Row>(){
	    	private final Logger log2 =  LoggerFactory.getLogger(Function.class);
			@Override
			public Row call(Row v1) throws Exception {
				// TODO Auto-generated method stub
				int id = v1.size();
				List<String> nStr = new ArrayList<String>();
				for(int i=1;i< id;i++){
					try{
						List<String> str = v1.getList(i);
						
//						log2.info("<<<<<<<<<<<< "+nStr.toString());
						for(String singlestr : str){
							try{
								String nstr = singlestr.replace("《", "").replace("》", "").replace(",", "").replace("（", "").replace("）", "").replace("，", "").replace(" 。", "").replace(" ", "").replace("：", "").replace("\n", "");
								if(nstr.length() >=2){
									nStr.add(nstr);
								}
							}catch(Exception e)
							{
								e.printStackTrace();
							}
						}
							
					}catch(Exception e)
						{
							e.printStackTrace();
						}
				}	
				Row r = RowFactory.create(nStr);
				log2.info("<<<<<<<<<<<< " + nStr.toString());
				return  nStr.size() > 0 ? r: null;
//				throw new  Exception("err");
			}
	    	
	    });
	 	Row zr = RowFactory.create(Arrays.asList(""));
	 	System.out.println("xxxxx "+ zr);
	    JavaRDD<Row> clearngramdatafilter = clearngramdata.filter(new Function<Row,Boolean>(){
	    	private final Logger log2 =  LoggerFactory.getLogger(Function.class);
			@Override
			public Boolean call(Row v1) throws Exception { 
				boolean f = false;
				try{
//					f = (v1.size() <= 2);
					f = (v1 == null);
					if(!f){
						log2.info(v1.size()+" good "+v1.toString());
					}
				}catch(Exception e){
					log2.error(v1.toString() + e.getMessage());
				}
				return !f;
			}
	    	
	    });
	    List<Row> lr = clearngramdatafilter.collect();
	    
	    for(Row r :lr){
	    	String singlestr =r.get(0).toString();
	    	System.out.println("!! "+singlestr+"</br>");
	    }
	    StructType schema = new StructType(new StructField[]{
	    		new StructField("words",DataTypes.createArrayType(DataTypes.StringType), false, Metadata.empty() )
	    });
	    
		Dataset<Row> documentDF = spark.createDataFrame(lr, schema);
		
		System.out.println("end --");
		
//	    // fit a CountVectorizerModel from the corpus
	    CountVectorizerModel cvModel = new CountVectorizer()
	      .setInputCol("words")
	      .setOutputCol("feature")
	      .setVocabSize(35)
	      .setMinDF(5)
	      .fit(documentDF);
//
//	    // alternatively, define CountVectorizerModel with a-priori vocabulary
//	    CountVectorizerModel cvm = new CountVectorizerModel(new String[]{"广", "东", "c"})
//	      .setInputCol("words")
//	      .setOutputCol("feature");
//
	   Dataset<Row> dr =  cvModel.transform(documentDF);
	   dr.show(false);
//	   dr.javaRDD().saveAsTextFile("/spark/cvmodel");
	
//	    // $example off$
	     

	    spark.stop();
	  }
}
