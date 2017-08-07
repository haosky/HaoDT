package crawler.contentextractor.webcollector;

import cn.edu.hfut.dmic.webcollector.util.FileUtils;
import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;

public class TestAppInterface {

	public static void testOA() {
		String APP_ID = "test";
		String ENCRYPTED_DYNAMIC_PASS = "";
		String to_user_id = "chendewei";
		String title = "测试程序接口自动启动流程";
		String FLOW_ID = "141";
		String xml = "";

		try {
			xml = FileUtils.read("C:\\Users\\Administrator\\Desktop\\OA备案\\OA备案\\备案系统\\74821397-81b6-4356-9837-5119141da17c.xml", "GBK");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		String iv = AESUtil.getRandomStr(16); //固定16字节
		String pass = AESUtil.getRandomStr(32);//32字节
		String method = "AES-256-CBC";

		//对称加密算法AES使用
		byte[] ivBytes = iv.getBytes();
		byte[] passBytes = pass.getBytes();

		String dynamicPass = pass + "," + iv + "," + method;
		//System.out.println("ENCRYPTED_DYNAMIC_PASS dynamic:" + dynamicPass);
		ENCRYPTED_DYNAMIC_PASS = RSAUtil.encrypt(dynamicPass, getPrivateKey());
		//System.out.println("ENCRYPTED_DYNAMIC_PASS encrypt:" + ENCRYPTED_DYNAMIC_PASS);
		ENCRYPTED_DYNAMIC_PASS = URLEncoder.encode(ENCRYPTED_DYNAMIC_PASS);
		//System.out.println("ENCRYPTED_DYNAMIC_PASS encode :" + ENCRYPTED_DYNAMIC_PASS);
		/*ENCRYPTED_DYNAMIC_PASS = URLDecoder.decode(ENCRYPTED_DYNAMIC_PASS);
		System.out.println("ENCRYPTED_DYNAMIC_PASS decode :" + ENCRYPTED_DYNAMIC_PASS);
		ENCRYPTED_DYNAMIC_PASS = RSAUtil.decrypt(ENCRYPTED_DYNAMIC_PASS, getPublicKey());
		System.out.println("ENCRYPTED_DYNAMIC_PASS decrypt:" + ENCRYPTED_DYNAMIC_PASS);*/

		to_user_id = AESUtil.encryptToStr(to_user_id.getBytes(), passBytes, ivBytes);
		//System.out.println("to_user_id encrypt:" + to_user_id);
		to_user_id = URLEncoder.encode(to_user_id);
		//System.out.println("to_user_id encode :" + to_user_id);
		/*to_user_id = URLDecoder.decode(to_user_id);
		System.out.println("to_user_id decode :" + to_user_id);
		to_user_id = AESUtil.decryptToStr(to_user_id, passBytes, ivBytes);
		System.out.println("to_user_id decrypt:" + to_user_id);*/

		title = AESUtil.encryptToStr(title.getBytes(), passBytes, ivBytes);
		//System.out.println("title encrypt:" + title);
		title = URLEncoder.encode(title);
		//System.out.println("title encode :" + title);
		/*title = URLDecoder.decode(title);
		System.out.println("title decode :" + title);
		title = AESUtil.decryptToStr(title, passBytes, ivBytes);
		System.out.println("title decrypt:" + title);*/

		FLOW_ID = AESUtil.encryptToStr(FLOW_ID.getBytes(), passBytes, ivBytes);
		//System.out.println("FLOW_ID encrypt:" + FLOW_ID);
		FLOW_ID = URLEncoder.encode(FLOW_ID);
		//System.out.println("FLOW_ID encode :" + FLOW_ID);
		/*FLOW_ID = URLDecoder.decode(FLOW_ID);
		System.out.println("FLOW_ID decode :" + FLOW_ID);
		FLOW_ID = AESUtil.decryptToStr(FLOW_ID, passBytes, ivBytes);
		System.out.println("FLOW_ID decrypt:" + FLOW_ID);*/

		xml = AESUtil.encryptToStr(xml.getBytes(), passBytes, ivBytes);
		//System.out.println("xml encrypt:" + xml);
		xml = URLEncoder.encode(xml);
		//System.out.println("xml encode :" + xml);
		/*xml = URLDecoder.decode(xml);
		System.out.println("xml decode :" + xml);
		xml = AESUtil.decryptToStr(xml, passBytes, ivBytes);
		System.out.println("xml decrypt:" + xml);*/

		// 创建参数队列
		List<NameValuePair> formparams = new ArrayList<NameValuePair>();
		formparams.add(new BasicNameValuePair("APP_ID", APP_ID));
		formparams.add(new BasicNameValuePair("ENCRYPTED_DYNAMIC_PASS", ENCRYPTED_DYNAMIC_PASS));
		formparams.add(new BasicNameValuePair("to_user_id", to_user_id));
		formparams.add(new BasicNameValuePair("title", title));
		formparams.add(new BasicNameValuePair("FLOW_ID", FLOW_ID));
		formparams.add(new BasicNameValuePair("xml", xml));
		
		postForm(formparams,"http://localhost/fsjc/Manager/MobileSvc/LoginSvc.asmx/App_interface");
	}

	/**
	 * post方式提交表单
	 */
	public static void postForm(List<NameValuePair> formparams, String webUrl) {
		// 创建默认的httpClient实例.    
		CloseableHttpClient httpclient = HttpClients.createDefault();
		// 创建httppost    
		HttpPost httppost = new HttpPost(webUrl);
		UrlEncodedFormEntity uefEntity;
		try {
			uefEntity = new UrlEncodedFormEntity(formparams, "UTF-8");
			httppost.setEntity(uefEntity);
			System.out.println("executing request " + httppost.getURI());
			CloseableHttpResponse response = httpclient.execute(httppost);
			try {
				HttpEntity entity = response.getEntity();
				if (entity != null) {
					System.out.println("--------------------------------------");
					System.out.println("Response content: " + EntityUtils.toString(entity, "UTF-8"));
					System.out.println("--------------------------------------");
				}
			} finally {
				response.close();
			}
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (UnsupportedEncodingException e1) {
			e1.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			// 关闭连接,释放资源    
			try {
				httpclient.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	public static String getPrivateKey() {
		String privateKey = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAKEPNyPD+taAXCfG" + "\r"
				+ "6dsqnv/h7zD9SZfHaOTqoQSfr23o3ZHWL8uZzINPXGv9PYAcY6Jc1DlXxbiIJpp4" + "\r" + "1rCLtolpGG1XHW44f/ZTfvx+xwQRIQbxcOqWXQYJ8HX9OMojZqK1VLNc61GzyRiA"
				+ "\r" + "ZTvx/tWYM2BciWTeB2GfOH66gRDLAgMBAAECgYBp4qTvoJKynuT3SbDJY/XwaEtm" + "\r"
				+ "u768SF9P0GlXrtwYuDWjAVue0VhBI9WxMWZTaVafkcP8hxX4QZqPh84td0zjcq3j" + "\r" + "DLOegAFJkIorGzq5FyK7ydBoU1TLjFV459c8dTZMTu+LgsOTD11/V/Jr4NJxIudo"
				+ "\r" + "MBQ3c4cHmOoYv4uzkQJBANR+7Fc3e6oZgqTOesqPSPqljbsdF9E4x4eDFuOecCkJ" + "\r"
				+ "DvVLOOoAzvtHfAiUp+H3fk4hXRpALiNBEHiIdhIuX2UCQQDCCHiPHFd4gC58yyCM" + "\r" + "6Leqkmoa+6YpfRb3oxykLBXcWx7DtbX+ayKy5OQmnkEG+MW8XB8wAdiUl0/tb6cQ"
				+ "\r" + "FaRvAkBhvP94Hk0DMDinFVHlWYJ3xy4pongSA8vCyMj+aSGtvjzjFnZXK4gIjBjA" + "\r"
				+ "2Z9ekDfIOBBawqp2DLdGuX2VXz8BAkByMuIh+KBSv76cnEDwLhfLQJlKgEnvqTvX" + "\r" + "TB0TUw8avlaBAXW34/5sI+NUB1hmbgyTK/T/IFcEPXpBWLGO+e3pAkAGWLpnH0Zh"
				+ "\r" + "Fae7oAqkMAd3xCNY6ec180tAe57hZ6kS+SYLKwb4gGzYaCxc22vMtYksXHtUeamo" + "\r" + "1NMLzI2ZfUoX";

		return privateKey;
	}

	public static String getPublicKey() {
		String publicKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQChDzcjw/rWgFwnxunbKp7/4e8w" + "\r"
				+ "/UmXx2jk6qEEn69t6N2R1i/LmcyDT1xr/T2AHGOiXNQ5V8W4iCaaeNawi7aJaRht" + "\r" + "Vx1uOH/2U378fscEESEG8XDqll0GCfB1/TjKI2aitVSzXOtRs8kYgGU78f7VmDNg"
				+ "\r" + "XIlk3gdhnzh+uoEQywIDAQAB" + "\r";

		return publicKey;
	}

	public static void main(String[] args) {
		testOA();
	}
}
