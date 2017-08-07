package hbasemodels;

import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.List;

import com.google.common.primitives.Bytes;

public class GuangDongFinancialPDFOP  extends BaseOP {

	public String title = "";
	public String organization = "";
	public String content = "";
	public String html = "";
	public String datetimestr = "";
	public String filename = "";
	public String letterto = "";
	public List<String> docs = null;
	
	public void setTitle(String title){
		this.title = title;
	}
	
	public void setFilename(String filename){
		this.filename = filename;
	}
	
	public void setLetterto(String letterto){
		this.letterto = letterto;
	}
	
	public void setHtml(String html){
		this.html = html;
	}
	
	public void setOrganization(String organization){
		this.organization = organization;
	}
	
	public void setDocs(List<String> docs){
		this.docs = docs;
	}
	
	public void setContent(String content){
		this.content = content;
	}
	
	public void setDatetimestr(String datetimestr){
		this.datetimestr = datetimestr;
	}
	
	public String getTitle(){
		return this.title;
	}
	
	public String getOrganization(){
		return this.organization;
	}
	
	public String getDatetimestr(){
		return this.datetimestr;
	}
	
	public String getContent(){
		return this.content;
	}
	
	public String getFilename(){
		return this.filename;
	}
	
	public String getHtml(){
		return this.html;
	}
	
	public String getLetterto(){
		return this.letterto;
	}
	
	public List<String> getDocs(){
		return this.docs;
	}
	
	public HashMap<String,Object> getMapKeyValue(){
		HashMap<String,Object> m = new HashMap<String,Object>();
		m.put("title",title);
		m.put("organization",organization);
		m.put("content",content);
		m.put("html",html);
		m.put("datetimestr",datetimestr);
		m.put("filename",filename);
		m.put("letterto",letterto);
		m.put("docs",docs);
		return m;
	}
	
	@Override
	public String toString(){
		return "GuangDongFinancialPDFOP [title=" + title + ", organization=" + organization +
				 ", filename=" + filename +
				  ", content=" + content +
				   ", html=" + html +
				    ", letterto=" + letterto +
				     ", docs=" + docs +
				     	", datetimestr=" + datetimestr + "]";
	}

	@Override
	public byte[] getRowKey() throws NoSuchAlgorithmException {
		// TODO Auto-generated method stub
		 return Bytes.concat(getFilename().getBytes());
	}
	
}
