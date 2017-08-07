package cushtml;
import java.io.File;
import java.io.IOException;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.encryption.InvalidPasswordException;
import org.apache.pdfbox.text.TextPosition;
import org.apache.pdfbox.tools.PDFText2HTML;
import customcommon.StrUtils;

public abstract class pdf2Html<T> extends PDFText2HTML{
	// T for bean Type
	
	public pdf2Html() throws IOException {
		super();
		// TODO Auto-generated constructor stub
	}
	
	public abstract T getExtraction();
	//定义内容提取方式
	

	public String getHtml(String file) throws InvalidPasswordException, IOException{
			PDDocument document = PDDocument.load(new File(file));
			pdf2Html stripper = this;
            stripper.setSortByPosition(true);
            stripper.setStartPage(0);
            stripper.setEndPage(document.getNumberOfPages());
            stripper.setAddMoreFormatting(true);
            stripper.getText(document).toCharArray();
            String htext = stripper.getText(document);
            document.close();
            
            return StrUtils.htmlEscapeText(htext);
	} 
	
 
	@Override
    protected void processTextPosition(TextPosition text)
    {
        super.processTextPosition(text);

    }
	
	
}
 