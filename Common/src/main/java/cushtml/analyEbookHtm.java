package cushtml;

import org.htmlparser.Node;
import org.htmlparser.Parser;
import org.htmlparser.filters.TagNameFilter;
import org.htmlparser.util.NodeList;
import org.htmlparser.util.ParserException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class analyEbookHtm implements analyBaseInterf{
    public static Logger LOG = LoggerFactory.getLogger(analyEbookHtm.class);
    private Parser parser = null;
    private String html = null;
    public void setAnalyParser(String htmlContent){
            this.html = htmlContent;
            this.parser = new Parser(); //Parser.createParser(htmlContent, "utf-8");
    }
    public String parsContent(){
        //提取tags
        TagNameFilter regerFilter = new TagNameFilter("BODY");

        // 得到所有经过过滤的标签，结果为NodeList
        StringBuilder sb = new StringBuilder();
        try{
            parser.setResource(this.html);
            NodeList list = parser.extractAllNodesThatMatch(regerFilter);
                for (int i = 0; i < list.size(); i++) {
                    Node tag = list.elementAt(i);
                        sb.append(tag.toPlainTextString());
            }
        }catch(ParserException e){
            e.printStackTrace();
            return null;
        }

        return sb.toString().trim();
    }

    public String parsTitle(){
        //提取tags
        TagNameFilter regerFilter = new TagNameFilter("TITLE");

        // 得到所有经过过滤的标签，结果为NodeList
        StringBuilder sb = new StringBuilder();
        try{
            parser.setResource(this.html);
            NodeList list = parser.extractAllNodesThatMatch(regerFilter);
            for (int i = 0; i < list.size(); i++) {
                Node tag = list.elementAt(i);
                sb.append(tag.toPlainTextString());
            }
        }catch(ParserException e){
            e.printStackTrace();
            return null;
        }
        return sb.toString().trim();
    }

    public analyEbookHtm anayToContent(File f){
        StringBuilder sb = new StringBuilder();
        try {
            InputStream is = new FileInputStream(f);
            InputStreamReader isr = new InputStreamReader(is, "gbk");
            BufferedReader br = new BufferedReader(isr);
            String s = null;
            while((s = br.readLine())!=null){
                s = s.replaceAll("&quot;","\"").replaceAll("&amp;","&").replaceAll("&lt;","<").replaceAll("&gt;",">").replaceAll("&nbsp;"," ");
                sb.append(s);
            }
            br.close();

        }catch (FileNotFoundException fe){
            LOG.error(fe.getMessage());
        }catch (IOException ie){
            LOG.error(ie.getMessage());
        }
        analyEbookHtm aeh = new analyEbookHtm();
        aeh.setAnalyParser(sb.toString());
        return aeh;
    }

    public static void main(String args[]){
            File f = new File("D:\\tmp\\zz2\\不爱我没关系_006.htm");

            analyEbookHtm aehM = new analyEbookHtm();
            analyEbookHtm aeh = aehM.anayToContent(f);

            String title = aeh.parsTitle();
            String content = aeh.parsContent();

            LOG.info(title);
            LOG.info(content);

    }
}
