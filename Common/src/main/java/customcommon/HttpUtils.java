package customcommon;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.NameValuePair;
import org.apache.commons.httpclient.methods.PostMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.xml.sax.SAXException;

import customcommon.HttpHeader;
 
public class HttpUtils {
		private static Logger logger = LoggerFactory.getLogger(HttpUtils.class);
		
	    public static String httpGet(String url,List<NameValuePair> params){
	        //get请求返回结果
	    	String strResult = null;
	        try {
	        	HttpClient client = new HttpClient();
	            //发送get请求
	        	PostMethod request = new PostMethod(url);
	        	
	        	request.addRequestHeader(new HttpHeader().setHeader("Content-type","text/xml;charset=utf8"));
	        	for(NameValuePair param:params)
	        		request.addParameter(param);	     	
	        	
	            int status_code = client.executeMethod(request);
	           
	            if (status_code == HttpStatus.SC_OK) {
	            	strResult = new String(request.getResponseBody(),"utf8");

	            } else {
	                logger.error("get请求提交失败:" + url);
	            }
	        } catch (IOException e) {
	            logger.error("get请求提交失败:" + url, e);
	        }
	        return strResult;
	    }

	    public static void main(String args[]) throws ParserConfigurationException, SAXException, IOException{
	    	ArrayList<NameValuePair> nvlist = new ArrayList<NameValuePair>();
	    	nvlist.add(new NameValuePair("x", "n"));
	    	nvlist.add(new NameValuePair("s", "我爱北京天安门"));
	    	nvlist.add(new NameValuePair("t", "all"));
        	
	    	String uri_base = "http://gx.master:9977/ltp";
	    	String rep = HttpUtils.httpGet(uri_base,nvlist);
	    	customcommon.xml.models.Nlpsent np = XmlUtils.parseNlpXml2Obj(rep);
	    	Iterator wlist = np.getWord();
	    	while(wlist.hasNext()){
	    		customcommon.xml.models.Nlpword word = (customcommon.xml.models.Nlpword)wlist.next();
	    		System.out.println(word.getCont());
	    	}
	    	
	    } 	

}
