package customcommon;

import org.apache.commons.httpclient.Header;

public class HttpHeader {
	
	public Header setHeader(String name,String value){
		Header header = new Header();
		header.setName(name);
		header.setValue(value);
		return header;
	}
	
}
