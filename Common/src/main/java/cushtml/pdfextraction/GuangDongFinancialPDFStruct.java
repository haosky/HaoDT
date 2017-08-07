package cushtml.pdfextraction;
import java.util.HashMap;
import java.util.List;

import cushtml.pdfextraction.BaseStruct;
public class GuangDongFinancialPDFStruct extends BaseStruct {
	
	private String title = "";
	private String organization = "";
	private String content = "";
	private String html = "";
	private String datetimestr = "";
	private String filename = "";
	private String letterto = "";
	private List<String> docs = null;
	
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
	
	public String toString(){
		// 只为打印的时候方便看
		return "GuangDongFinancialPDFStruct:{\"title\":\""+title+"\",\n\n"
				+ "\"organization\":\""+organization+"\",\n\n"
				+ "\"datetimestr\":\""+datetimestr+"\",\n\n"
				+ "\"filename\":\""+filename+"\",\n\n"
				+ "\"content\":\""+content+"\",\n\n"
				+ "\"html\":\""+html+"\"\n\n"
				+ "\"letterto\":\""+letterto+"\"\n\n"
				+ "\"docs\":\""+docs+"\"\n\n"
				+ "}";
	}
	

}
