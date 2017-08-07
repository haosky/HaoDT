package org.gx.intell.Query;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gxthrift.simhandler.sim_develop;


public class ContentSimQuery
{	
	public static Logger LOG = LoggerFactory.getLogger(ContentSimQuery.class);
	sim_develop.Client client = null; 
	TSocket transport = null;
	
	public ContentSimQuery(){
		
		if(this.transport == null || this.client == null ||!transport.isOpen()){
			Properties prop = new Properties();
			InputStream ins = ContentSimQuery.class.getClassLoader().getResourceAsStream("tserverSettings.properties");
			try {
				prop.load(ins);
				this.transport  =new TSocket(prop.getProperty("gxthrift.sim_develop.host"),
							Integer.parseInt(prop.getProperty("gxthrift.sim_develop.port")));
//				this.transport  =new TSocket("192.168.18.236",
//						9994);
				transport.open();
			} catch (TTransportException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				LOG.error(e.getMessage());
			}
			TProtocol protocol = new TBinaryProtocol(transport);
			this.client = new sim_develop.Client(protocol);
	    }
	}
	

	public String getConentSimHash(String art_content){
		String simcode = null;
		try {
			simcode = this.client.get_art_sim(art_content);
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			LOG.error(e.getMessage());
		}
		destory();
		return simcode;		
	}
	
	//  
	public String getDiffArtList(){
		String list = "[]";
		try {
			list = this.client.get_differencelist();
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			LOG.error(e.getMessage());
		}
		destory();
		return list;		
	}
	 
	//相似详情
	public String getSimInfo(String docid){
		String result = "{}";
		try {
			result = this.client.get_differenceinfo(docid);
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	// 相似片段
	public String getSimParse(String docid){
		String result = "{}";
		try {
			result = this.client.get_differenceparse(docid);
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	// 综合评价
	public String getSimComment(String docid){
		String result = "{}";
		try {
			result = this.client.get_differencecomment(docid);
		} catch (TException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	// 差异对比
	public String calc2DocSimById(String leftDocId,String rightDocId){
		String result="{}";
		try {
			result = this.client.get_different_2_docid(leftDocId, rightDocId);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	// 搜索列表
	public String getSameDocListBySearch(String searchStat){
		String result="[]";
		try {
			result = this.client.get_same_list(searchStat);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	// 搜索列表
	public String getSameAll(String DocId,String UserIP){
		/** DocId 文档ID
		UserIP 提供客户端使用者的ip地址 **/
		
		String result= null;
		try {
			result = this.client.get_doc_same_all(DocId, UserIP);
		} catch (TException e) {
			// TODO Auto-generated catch block
			LOG.error(e.getMessage());
		}
		destory();
		return result;	
	}
	
	public void destory(){
		try{
			this.transport.close();
		}catch(Exception e){
			LOG.error(e.getMessage());
		}
		this.client = null;
	}
	
    public static void main( String[] args )
    {   

//    	String str = new ContentSimQuery().calc2DocSimById("10003899642146308774bbe80347dc6dd43e545ae3ec25430c89","1000389964214630877431e318dcd34c335b75e47aaa32462c37");
//    	String str = new ContentSimQuery().getSimComment("10003899642k146308774bbe80347dc6dd43e545ae3ec25430c89");
//    	String str = new ContentSimQuery().getSimParse("10003899642146308774bbe80347dc6dd43e545ae3ec25430c89");
//    	String str = new ContentSimQuery().getSimInfo("10003899642146308774bbe80347dc6dd43e545ae3ec25430c89");
    	String str = new ContentSimQuery().getSameAll("1000389964214630877431e318dcd34c335b75e47aaa32462c37","192.168.12.123");
    	System.out.println(str);
    }
}


