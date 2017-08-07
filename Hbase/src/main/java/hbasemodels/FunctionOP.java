package hbasemodels;
import java.io.Serializable;
import java.security.NoSuchAlgorithmException;

import com.google.common.primitives.Bytes;
import customcommon.StrUtils;

/**
 * Created by gxkj-941 on 2017/4/5.
 */
public class FunctionOP extends BaseOP{
    public String title;
    public String subTitle;
    public String content;

    public FunctionOP() {
        super();
    }
    public FunctionOP(String title, String subTitle, String content) {
        super();
        this.title = title;
        this.subTitle = subTitle;
        this.content = content;
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

    @Override
    public byte[] getRowKey() throws NoSuchAlgorithmException{
        return Bytes.concat(StrUtils.toMd5(getTitle()),StrUtils.toMd5(getSubTitle()));
    }
}
