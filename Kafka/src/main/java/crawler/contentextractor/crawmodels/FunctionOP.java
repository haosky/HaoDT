package crawler.contentextractor.crawmodels;
import java.io.Serializable;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionOP implements Serializable{
    private String title;
    private String subTitle;
    private String content;

    public FunctionOP() {
        super();
    }
    public FunctionOP(String title, String subTitle, String content) {
        super();
        this.title = title;
        this.subTitle = subTitle;
        this.subTitle = subTitle;
    }
    @Override
    public String toString() {
        return "FunctionOP [title=" + title + ", subTitle=" + subTitle + ", content=" + content + "]";
    }

    public String getTitle(){
        return this.title;
    }

    public String getSubTitle(){
        return this.subTitle;
    }

    public String getContent(){
        return this.content;
    }

    public void setTitle(String title){
        this.title = title;
    }
    public void setSubTitle(String subTitle){
        this.subTitle = subTitle;
    }
    public void setContent(String content){
        this.content = content;
    }
}
