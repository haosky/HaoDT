package mongotablesv1;
import customcommon.MongoDBUtils;
import hbaseutils.HbaseDao;

import org.bson.BsonArray;
import org.bson.BsonDocument;
import org.bson.Document;
import org.bson.codecs.configuration.CodecRegistry;

import java.util.Iterator;
import java.util.ArrayList;
import org.bson.conversions.Bson;

import com.mongodb.Block;
import com.mongodb.async.SingleResultCallback;
import com.mongodb.async.client.FindIterable;

import com.mongodb.async.client.MongoClient;
import com.mongodb.async.client.MongoCollection;
import com.mongodb.async.client.MongoDatabase;


public class MongoDB2Hbase2 {
	
	
	
	public static void main(String args[]){
//		HbaseDao hdao = new HbaseDao();
		MongoDBUtils mdbutils = new MongoDBUtils();
		try{
			MongoClient mc = mdbutils.createClient("mongodb://admin:tingting@192.168.1.12:27020/admin?connectTimeoutMS=30000&maxIdleTimeMS=600000&authMechanism=SCRAM-SHA-1");
			MongoDatabase mdatabase = mc.getDatabase("DStore");
			MongoCollection<Document> mcollection = mdatabase.getCollection("BILL_SOURCE_TAB");
			
			 
			SingleResultCallback<Void> callback = new SingleResultCallback<Void>(){
	
				@Override
				public void onResult(Void arg0, Throwable arg1) {
					// TODO Auto-generated method stub
					System.out.println("Operation Finished!");
					arg1.printStackTrace();
					
				}
				
			};
			Block<Document> printDocumentBlock = new Block<Document>() {
			    @Override
			    public void apply(final Document document) {
			        System.out.println(document.toJson());
			    }
			};
	 
			mcollection.find( ).forEach(printDocumentBlock, callback);;
		 
		  
		}catch(Exception e){
			e.printStackTrace();
		}
		finally{
			mdbutils.destory();
		}
	}

	private static void find() {
		// TODO Auto-generated method stub
		
	}
}
