package DFlow;
import com.huaban.analysis.jieba.JiebaSegmenter;
import org.apache.spark.SparkContext;
import org.apache.spark.api.java.*;
import org.apache.spark.api.java.function.Function;
import org.apache.spark.api.java.function.Function2;
import org.apache.spark.graphx.*;
import org.apache.spark.ml.feature.Word2Vec;
import org.apache.spark.ml.feature.Word2VecModel;
import org.apache.spark.ml.linalg.Vector;
import org.apache.spark.rdd.RDD;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.*;
import org.apache.spark.storage.StorageLevel;
import scala.Tuple2;
import scala.reflect.ClassTag;
import scala.reflect.ClassTag$;
import scala.runtime.AbstractFunction1;
import scala.runtime.AbstractFunction2;
import scala.runtime.BoxedUnit;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by hao on 2017/3/20.
 * spark ml.feature of word2vec and GraphX
 */
public class Word2vecGraphX {
    static abstract class SerializableFunction1<T1,R>
            extends AbstractFunction1<T1,R> implements Serializable {}
    static abstract class SerializableFunction2<T1,T2,R>
            extends AbstractFunction2<T1,T2,R> implements Serializable {}

    private static final String ARTPATH = "";
    public static String listToString(List list, String separator) {
        StringBuilder sb = new StringBuilder();
        for(int i = 0; i < list.size(); i++) {
            sb.append(list.get(i)).append(separator);
        }
        return sb.toString().substring(0,sb.toString().length()-1);
    }

    public static List<String> jiebaToken(String sentence){
        JiebaSegmenter segmenter = new JiebaSegmenter();
        List<String> tokenlist = segmenter.sentenceProcess(sentence);
        return  tokenlist;
    }

    public static String makeArticle(String filePath){
        String s2l ="这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。\n" +
                "我不喜欢日本和服。"+"雷猴回归人间。\n"+
                "工信部干事每月都要经过下属科室都要亲自交代24种交换机等技术性器件的安装工作\n"+
                "结果婚的和尚未结过婚的" ;
        return s2l;
    }

    public static void main(String[] args) {
        SparkSession spark = SparkSession
                .builder()
                .appName("W2vg")
                .getOrCreate();
        String art = makeArticle(ARTPATH);

        List<Row> data = new ArrayList<Row>();
        for(String line:art.split("\n")){
            data.add(RowFactory.create(jiebaToken(line)));
        }

        StructType schema = new StructType(new StructField[]{
                new StructField("text", new ArrayType(DataTypes.StringType, true), false, Metadata.empty())
        });
        Dataset<Row> documentDF = spark.createDataFrame(data, schema);

        Word2Vec word2Vec = new Word2Vec()
                .setInputCol("text")
                .setOutputCol("result")
                .setVectorSize(3)
                .setMinCount(0);

        Word2VecModel model = word2Vec.fit(documentDF);
        Dataset<Row> result = model.transform(documentDF);

        for (Row row : result.collectAsList()) {
            List<String> text = row.getList(0);
            Vector vector = (Vector) row.get(1);

            System.out.println("Text: " + text + " => \nVector: " + vector + "\n");
        }
        Dataset<Row> fresult = model.findSynonyms("我",13);
        SparkContext psc  = spark.sparkContext();
        JavaSparkContext sc = JavaSparkContext.fromSparkContext(psc);
        List<Tuple2<Object,String>> verclist = new ArrayList<Tuple2<Object,String>>();
        List<Edge<Double>> edlist = new ArrayList<Edge<Double>>();

        for (Row row : fresult.collectAsList()) {
            String word = row.getString(0);
            double distinct = row.getDouble(1);
            verclist.add(new Tuple2<Object,String>(new Long(word.hashCode()),word));
            edlist.add(new Edge<Double>(new Long(word.hashCode()), new Long("我".hashCode()), distinct));
        }
        JavaRDD<Tuple2<Object, String>> myVertices = sc.parallelize(verclist);
        JavaRDD<Edge<Double>> myEdges = sc.parallelize(edlist);

        Graph<String,Double> myGraph = Graph.apply(myVertices.rdd(),
                myEdges.rdd(), "", StorageLevel.MEMORY_ONLY(),
                StorageLevel.MEMORY_ONLY(), tagString, tagDouble);

        Graph<Long,Double> initialGraph = myGraph.mapVertices(
                new SerializableFunction2<Object,String,Long>() {
                    public Long apply(Object o, String s) {
                        return 0L; }
                },
                tagLong, null);

        initialGraph.vertices().saveAsObjectFile("mayGrapthVertices");
        initialGraph.edges().saveAsTextFile("mayGrapthEdges");
//        initialGraph.vertices().saveAsTextFile("mayGrapthVertices");
        List<Tuple2<Object,Long>> ls = toJavaPairRDD(
                propagateEdgeCount(initialGraph).vertices(), tagLong).collect();

        for (Tuple2<Object,Long> t : ls)
            System.out.print(t);
        System.out.println();
    // Must explicitly provide for implicit Scala parameters in various
    // sendMsg
//        // 写入本地
//        try {
//            model.write().overwrite().save("sz");
//        }catch(Exception e){
//            e.printStackTrace();
//        }
        sc.stop();
    }

    // function calls
    private static final ClassTag<Long> tagLong =
            ClassTag$.MODULE$.apply(Long.class);

    private static final ClassTag<Double> tagDouble =
            ClassTag$.MODULE$.apply(Double.class);

    private static final ClassTag<String> tagString =
            ClassTag$.MODULE$.apply(String.class);
    private static final ClassTag<Object> tagObject =
            ClassTag$.MODULE$.apply(Object.class);

    // sendMsg
    private static final SerializableFunction1<EdgeContext<Long, Double, Long>, BoxedUnit> sendMsg =
            new SerializableFunction1<
                    EdgeContext<Long, Double, Long>, BoxedUnit>() {
                public BoxedUnit apply(EdgeContext<Long, Double, Long> ec) {
                    ec.sendToDst(ec.srcAttr()+1L);
                    return BoxedUnit.UNIT;
                }
            };

    // mergeMsg
    private static final SerializableFunction2<Long, Long, Long>
            mergeMsg = new SerializableFunction2<Long, Long, Long>() {
        public Long apply(Long a, Long b) {
            return Math.max(a,b);
        }
    };

    private static <T> JavaPairRDD<Object,T>
    toJavaPairRDD(VertexRDD<T> v, ClassTag<T> tagT) {
        return new JavaPairRDD<Object,T>((RDD<Tuple2<Object,T>>)v,
                tagObject, tagT);
    }

    private static Graph<Long,Double> propagateEdgeCount(
            Graph<Long,Double> g) {
        VertexRDD<Long> verts = g.aggregateMessages( sendMsg, mergeMsg, TripletFields.All, tagLong);
        Graph<Long,Double> g2 = Graph.apply(
                verts
                , g.edges()
                , 0L
                ,StorageLevel.MEMORY_ONLY()
                , StorageLevel.MEMORY_ONLY()
                ,tagLong
                , tagDouble);
        Long check = toJavaPairRDD(g2.vertices(), tagLong)
                .join(toJavaPairRDD(g.vertices(), tagLong))
                .map(new Function<Tuple2<Object,Tuple2<Long,Long>>,
                        Long>() {
                    public Long call(Tuple2<Object,Tuple2<Long,Long>> t) {
                        return t._2._1 - t._2._2;
                    }
                })
                .reduce(new Function2<Long, Long, Long>() {
                    public Long call(Long a, Long b) {
                        return (a+b);}
                });
        if (check > 0)
            return propagateEdgeCount(g2);
        else
            return g;
    }
}


