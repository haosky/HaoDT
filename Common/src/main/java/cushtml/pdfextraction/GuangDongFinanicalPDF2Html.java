package cushtml.pdfextraction;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;

import org.apache.pdfbox.pdmodel.encryption.InvalidPasswordException;
import org.htmlparser.Node;
import org.htmlparser.Parser;
import org.htmlparser.filters.TagNameFilter;
import org.htmlparser.util.NodeList;
import org.htmlparser.util.ParserException;

import customcommon.StrUtils;
import cushtml.pdf2Html;
import cushtml.pdfextraction.GuangDongFinancialPDFStruct;
public class GuangDongFinanicalPDF2Html extends pdf2Html<GuangDongFinancialPDFStruct> {
	
	private Parser parser = null;
    private String html = null;
    private String bodystr = null;
    private String filename = null;
    public  GuangDongFinanicalPDF2Html(String file)  throws IOException {
    		super();
            this.html = getHtml(file);
            this.parser = new Parser();  
            this.filename = file;
            if(file.contains(java.io.File.separator))
            	this.filename = file.substring(file.lastIndexOf(java.io.File.separator)+1);       
    }
    
    @SuppressWarnings("unused")
	public String getHtml(String file) throws InvalidPasswordException, IOException{
    	return super.getHtml(file);
    }
	
    public String getHtmlContent(){
    	return this.html;
    }
    
	@SuppressWarnings("unused")
	private GuangDongFinanicalPDF2Html() throws IOException {
		super();
	}

	@Override
	public GuangDongFinancialPDFStruct getExtraction() {
		// TODO Auto-generated method stub
		
		String pdfcontent = getBodyContent();
		String html = getHtmlContent();
		String title = getTitleFromBody(pdfcontent);
		String datetimestr = getDatetimestrFromBody(pdfcontent);
		String organization = getOrganizationFromBody(pdfcontent);
		String content = getContentFromBody(pdfcontent, title, organization,datetimestr);
		String letterto = getLittleToFromContent(pdfcontent);
		List<String> docs = getDocsFromContent(pdfcontent);
		
		GuangDongFinancialPDFStruct gdstruct = new GuangDongFinancialPDFStruct();
		gdstruct.setTitle(title);
		gdstruct.setContent(content);
		gdstruct.setDatetimestr(datetimestr == null?null:datetimestr.replaceAll(" ",""));
		gdstruct.setFilename(this.filename);
		gdstruct.setHtml(html);
		gdstruct.setOrganization(organization);
		gdstruct.setLetterto(letterto); 
		gdstruct.setDocs(docs);
		return gdstruct;
	}
	
	private String getTitleFromBody(String pdfcontent){ 
		Matcher fix = StrUtils.reToMatcher(pdfcontent, ".*：");
		String title = "";
		if(fix.find()){
			String prestr = fix.group(0);
			title = pdfcontent.substring(0,pdfcontent.indexOf(prestr));
		}
		return title.trim();
	}
	
	
	private String getDatetimestrFromBody(String pdfcontent){
		Matcher fix = StrUtils.reToMatcher(pdfcontent, "(.+\\s*\\n"+
"\\s*\\n)"+
"\\s*(\\s*\\d{4}\\s*年\\s* \\d{1,2}\\s*月\\s* \\d{1,2}\\s*日)");
		String Datetimestr = null;
		if(fix.find()){
			Datetimestr = fix.group(2);
		}
		return Datetimestr;
	}
	
	private String getContentFromBody(String pdfcontent,String title,String organization,String datetimestr){
		String content = pdfcontent;
		if(pdfcontent.startsWith(title)){
			content = pdfcontent.replace(title, "").trim();
		}
		
		Matcher fix = StrUtils.reToMatcher(pdfcontent,"\\n\\s*"+organization+"\\s*\\n\\s*"+datetimestr);
		if(fix.find()){
			content = content.substring(0, content.lastIndexOf(fix.group(0)));
		}
		return content;
	}
	
	private String getOrganizationFromBody(String pdfcontent){
		Matcher fix = StrUtils.reToMatcher(pdfcontent, "(.+\\s*\\n"+
"\\s*\\n)"+
				"\\s*(\\s*\\d{4}\\s*年\\s* \\d{1,2}\\s*月\\s* \\d{1,2}\\s*日)");
		String organization = null;
		if(fix.find()){
			organization = fix.group(1).trim();
		}
		return organization;
	}
	
	private String getLittleToFromContent(String content){
		return content.substring(0,content.indexOf("： "));
	}
	
	private List<String> getDocsFromContent(String content){
		List<String> listDoc = new ArrayList<String>();
		String sucontent = content.replace("\n", "").replace(" ", "").replace("\r", "");
		Matcher fix = StrUtils.reToMatcher(sucontent, "《([^》]+)》");
		while(fix.find()){
			for(int i=1; i<=fix.groupCount();i++){
					listDoc.add(fix.group(1));
			}
			
		}
		return listDoc;
	}
	
	private String getBodyContent(){
		TagNameFilter regerFilter = new TagNameFilter("BODY");
		
        // 得到所有经过过滤的标签，结果为NodeList
        StringBuilder sb = new StringBuilder();
        try{
            parser.setResource(this.html);
            NodeList list = parser.extractAllNodesThatMatch(regerFilter);
                for (int i = 0; i < list.size(); i++) {
                    Node tag = list.elementAt(i);
                    String p = tag.toPlainTextString();
                    Matcher a = StrUtils.reToMatcher(p, "(\\s+-\\s+\\d+\\s+-\\s+\n)");
                    p = a.replaceAll("\n");
                    sb.append(p);
            }
        }catch(ParserException e){
            e.printStackTrace();
            return null;
        }
        String bodyText = sb.toString();
        bodyText = bodyText.replace("广东省财政厅文件", "");
        Matcher a = StrUtils.reToMatcher(bodyText, "(粤财[^\\n]+号\\s+\\n)|(.\\s+急\\s+\\n)|(.\\s+急\\s+粤财[^\\n]+号\\s+\\n)|\\s+以此件为准\\s+\\n");
        bodyText = a.replaceAll("");
        return bodyText.trim();
	}
	
 
	public static void main(String args[]) throws IOException{
		GuangDongFinanicalPDF2Html g = new GuangDongFinanicalPDF2Html("D:\\workspace\\budgetNum\\OA569714.pdf");
		String pdfcontent = g.getBodyContent();
		System.out.println(pdfcontent.replace("\n", "").replace(" ", "").replace("\r", ""));
		System.out.println(g.getLittleToFromContent(pdfcontent));
		System.out.println(g.getDocsFromContent(pdfcontent));
		
	}
	
}
