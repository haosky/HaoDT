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
import cushtml.pdfextraction.GuangDongSpecFinanicalPDF2Struct_V1;
public class GuangDongSpecFinanicalPDF2Html_V1 extends pdf2Html<GuangDongSpecFinanicalPDF2Struct_V1> {
	//"project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"
	private Parser parser = null;
    private String html = null;
    private String bodystr = null;
    private String filename = null;
    public  GuangDongSpecFinanicalPDF2Html_V1(String file)  throws IOException {
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
	private GuangDongSpecFinanicalPDF2Html_V1() throws IOException {
		super();
	}

	@Override
	public GuangDongSpecFinanicalPDF2Struct_V1 getExtraction() {
		// TODO Auto-generated method stub
		
		String pdfcontent = getBodyContent(); 
		GuangDongSpecFinanicalPDF2Struct_V1 gdstruct = new GuangDongSpecFinanicalPDF2Struct_V1();
		String[] filenamesplit = splitFileName(this.filename);
		gdstruct.setProject(filenamesplit[1].replaceAll(".pdf", ""));
		gdstruct.setUuid(filenamesplit[0]);
		gdstruct.setContent(pdfcontent);
		
		return gdstruct;
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
        Matcher a = StrUtils.reToMatcher(bodyText, "(\\s+\\n)");
        bodyText = a.replaceAll("\n"); 
        return bodyText.trim();
	}
	
	private String[] splitFileName(String fileName){
		if(fileName.contains("_") )
			return fileName.split("_");
		String startPrex = "0123456789-()";
		char[] carset = fileName.toCharArray();
		int i = 0;
		for(char c : carset){
			if(! startPrex.contains(c+""))
				break;
			i+=1;
		}
		try{
		String[] result = {fileName.substring(0,i-1),fileName.substring(i)};
		return result;
		}catch(Exception e){
			e.printStackTrace();
		}
		return null;
	}
	
	public static void main(String args[]) throws IOException{
		GuangDongSpecFinanicalPDF2Html_V1 g = new GuangDongSpecFinanicalPDF2Html_V1("E:\\专项资金\\uploads\\38527564477594137774佐证材料.pdf");
		GuangDongSpecFinanicalPDF2Struct_V1 gstruct = g.getExtraction();
		System.out.println(gstruct.toString());
	}
	
}
