package  cushtml.pdfextraction;

import java.util.HashMap;
import java.util.List;
public class GuangDongSpecFinanicalPDF2Struct_V1 extends BaseStruct {
	//"project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"
	private String project = "";
	private String uuid = "";
	private String finical_unit = "";
	private String content = "";
	private String finical_name = "";
	private String date = "";
	private String doc = "";
	private String unit = "";
	private String finical = "";
	private String fl_type = "";
	private String submiter = "";
	 
	
	public void setProject(String project){
		this.project = project;
	}
	
	public void setUuid(String uuid){
		this.uuid = uuid;
	}
	
	public void setDoc(String doc){
		this.doc = doc;
	}
	
	public void setUnit(String unit){
		this.unit = unit;
	}
	
	public void setFinical_name(String finical_name){
		this.finical_name = finical_name;
	}
	
	public void setFinical_unit(String finical_unit){
		this.finical_unit = finical_unit;
	}
	
 	
	public void setContent(String content){
		this.content = content;
	}
	
	public void setDate(String date){
		this.date = date;
	}
	
	public void setFinical(String finical){
		this.finical = finical;
	} 
	
	public void setFl_type(String fl_type){
		this.fl_type = fl_type;
	}
	
	public void setSubmiter(String submiter){
		this.submiter = submiter;
	}
	
	public String getProject(){
		return this.project;
	}
	
	public String getUuid(){
		return this.uuid;
	}
	
	public String getFinical_unit(){
		return this.finical_unit;
	}
	
	public String getDate(){
		return this.date;
	}
	
	public String getContent(){
		return this.content;
	}
	
	public String getDoc(){
		return this.doc;
	}
	
	public String getFinical_name(){
		return this.finical_name;
	}
	
	public String getUnit(){
		return this.unit;
	}
	
	public String getFinical(){
		return this.finical;
	}
	
	public String getFl_type(){
		return this.fl_type;
	}
	
	public String getSubmiter(){
		return this.submiter;
	}
	public HashMap<String,Object> getMapKeyValue(){
		HashMap<String,Object> m = new HashMap<String,Object>();
		m.put("project",project);
		m.put("uuid",uuid);
		m.put("finical_unit",finical_unit);
		m.put("content",content);
		m.put("finical_name",finical_name);
		m.put("date",date);
		m.put("doc",doc);
		m.put("unit",unit);
		m.put("finical",finical);
		m.put("fl_type",fl_type);
		m.put("submiter",submiter);
		return m;
	}
	
	public String toString(){
		// 只为打印的时候方便看
		return "GuangDongFinancialPDFStruct:{\"project\":\""+project+"\",\n\n"
				+ "\"uuid\":\""+uuid+"\",\n\n"
				+ "\"finical_unit\":\""+finical_unit+"\",\n\n"
				+ "\"content\":\""+content+"\",\n\n"
				+ "\"finical_name\":\""+finical_name+"\"\n\n"
				+ "\"date\":\""+date+"\"\n\n"
				+ "\"doc\":\""+doc+"\"\n\n"
				+ "\"unit\":\""+unit+"\"\n\n"
				+ "\"finical\":\""+finical+"\"\n\n"
				+ "\"fl_type\":\""+fl_type+"\"\n\n"
				+ "\"submiter\":\""+submiter+"\"\n\n"
				+ "}";
	}
	

}
