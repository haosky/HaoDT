package hbasemodels;
import java.io.Serializable;

import com.google.common.primitives.Bytes;
import customcommon.StrUtils;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionKeyWordOP extends BaseOP{
    public String title;
    public String subTitle;
    public String keywords;

    public FunctionKeyWordOP() {
        super();
    }
    public FunctionKeyWordOP(String title, String subTitle, String keywords) {
        super();
        this.title = title;
        this.subTitle = subTitle;
        this.keywords = keywords;
    }
    @Override
    public String toString() {
        return "FunctionKeyWordOP [title=" + title + ", subTitle=" + subTitle + ", keywords=" + keywords + "]";
    }

    public String getTitle(){
        return this.title;
    }

    public String getSubTitle(){
        return this.subTitle;
    }

    public String getKeyWords(){
        return this.keywords;
    }

    public void setTitle(String title){
        this.title = title;
    }
    public void setSubTitle(String subTitle){
        this.subTitle = subTitle;
    }
    public void setKeyWords(String keywords){
        this.keywords = keywords;
    }

    @Override
    public byte[] getRowKey(){
        return Bytes.concat(getTitle().getBytes(),getSubTitle().getBytes());
    }
}
