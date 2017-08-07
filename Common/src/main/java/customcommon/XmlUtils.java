package customcommon;

import org.apache.commons.digester3.Digester;
import org.xml.sax.SAXException;

import java.io.IOException;
import org.xml.sax.InputSource;
import java.io.StringReader;
import javax.xml.parsers.ParserConfigurationException;
import customcommon.xml.models.Nlpsent;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
 
/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class XmlUtils {
	public static Log log = LogFactory.getLog(XmlUtils.class);
	
	public static Nlpsent parseNlpXml2Obj(String xmlstr) throws ParserConfigurationException, SAXException, IOException{
		StringReader sr = new StringReader(xmlstr);   
		InputSource is = new InputSource(sr);  
		Digester digester = new Digester();
		digester.setValidating(false);
		digester.addObjectCreate("xml4nlp/doc/para/sent", "customcommon.xml.models.Nlpsent");
		digester.addSetProperties("xml4nlp/doc/para/sent");
		digester.addObjectCreate("xml4nlp/doc/para/sent/word", "customcommon.xml.models.Nlpword");
		digester.addSetProperties("xml4nlp/doc/para/sent/word");
		digester.addSetNext("xml4nlp/doc/para/sent/word", "addWord", "customcommon.xml.models.word");		
		digester.addObjectCreate("xml4nlp/doc/para/sent/word/arg", "customcommon.xml.models.Nlparg");
		digester.addSetProperties("xml4nlp/doc/para/sent/word/arg");
		digester.addSetNext("xml4nlp/doc/para/sent/word/arg", "addArg", "customcommon.xml.models.Nlparg");
		Nlpsent np = digester.parse(is);
		return  np;
	}
	
	public static void main(String args[]) {
		String xmlstr = "<xml4nlp>\n"+
    "<note sent=\"y\" word=\"y\" pos=\"y\" ne=\"y\" parser=\"y\" wsd=\"n\" srl=\"y\" />\n"+
    "<doc>\n"+
        "<para id=\"0\">\n"+
        "<sent id=\"0\" cont=\"我爱北京天安门\">\n"+
//        "<word id=\"0\" cont=\"我\" pos=\"r\" ne=\"O\" parent=\"1\" relate=\"SBV\" />\n"+
        "<word id=\"1\" cont=\"爱\" pos=\"v\" ne=\"O\" parent=\"-1\" relate=\"HED\">\n"+
        "<arg id=\"0\" type=\"A0\" beg=\"0\" end=\"0\" /> \n "+
        "<arg id=\"1\" type=\"A1\" beg=\"2\" end=\"3\" /> \n "+
        "</word>\n"+
        "<word id=\"2\" cont=\"北京\" pos=\"ns\" ne=\"B-Ns\" parent=\"3\" relate=\"ATT\" />\n"+
        "<word id=\"3\" cont=\"天安门\" pos=\"ns\" ne=\"E-Ns\" parent=\"1\" relate=\"VOB\" />\n"+
        "</sent>\n"+
        "</para>\n"+
        "</doc>\n"+
        "</xml4nlp>";
		log.info(xmlstr);
		try {
			System.out.println(parseNlpXml2Obj(xmlstr));
		} catch (ParserConfigurationException | SAXException | IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
