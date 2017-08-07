package customcommon;

import java.io.UnsupportedEncodingException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.seg.common.Term;
import com.huaban.analysis.jieba.JiebaSegmenter;
import com.huaban.analysis.jieba.JiebaSegmenter.SegMode;
import com.huaban.analysis.jieba.SegToken;
import com.huaban.analysis.jieba.WordDictionary;
import org.apache.commons.lang.StringEscapeUtils;
/**
 * Created by gxkj-941 on 2017/3/31.
 */
public class StrUtils {
	private static final boolean IS_WINDOWS = System.getProperty( "os.name" ).contains( "indow" );
	private static Path dictpath = null;
	private static String dictpathstr = StrUtils.class.getClassLoader().getResource("userdict.txt").getPath();
	static {
		dictpathstr = IS_WINDOWS ? dictpathstr.substring(1) : dictpathstr;
		dictpath = Paths.get(dictpathstr);
	}
    public static boolean reMatcher(String strput,String regex){
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(strput);
		return matcher.matches();
    }
    
    public static Matcher reToMatcher(String strput,String regex){
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(strput);
        return matcher;
    }

    public static byte[] toMd5(String str) throws NoSuchAlgorithmException{
        MessageDigest md = MessageDigest.getInstance("MD5");
        md.update(str.getBytes());
        return md.digest();
    }
    
    public static String toMd5Str(String str) throws NoSuchAlgorithmException, UnsupportedEncodingException{
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] bs = md.digest(str.getBytes());
        StringBuilder sb = new StringBuilder(40);
        for(byte x:bs) {
            if((x & 0xff)>>4 == 0) {
                sb.append("0").append(Integer.toHexString(x & 0xff));
            } else {
                sb.append(Integer.toHexString(x & 0xff));
            }
        }
        return sb.toString().trim();

    }
    
    public static int toUUID(String str) throws NoSuchAlgorithmException, UnsupportedEncodingException{
    	
        return UUID.fromString(str).variant();   
    }
    
    public static List<String> jiebaToken(String sentence){
		WordDictionary.getInstance().loadUserDict(dictpath);
        JiebaSegmenter segmenter = new JiebaSegmenter();
        List<String> tokenlist = segmenter.sentenceProcess(sentence);
        return  tokenlist;
    }
    
    public static List<SegToken> jiebaSegToken(String sentence){
		WordDictionary.getInstance().loadUserDict(dictpath);
        JiebaSegmenter segmenter = new JiebaSegmenter();
		List<SegToken> tokenlist = segmenter.process(sentence, SegMode.SEARCH);
        return  tokenlist;
    }
    
    public static List<Term> hanlpToken(String sentence){
    	List<Term> keywordList = HanLP.newSegment().enableAllNamedEntityRecognize(true).seg(sentence);
    	return keywordList;
    }
    
    public static List<String> extractKeyWord(String article,int count){
    	List<String> keywordList = HanLP.extractKeyword(article, count);
    	return keywordList;
    }
    
    public static String[] patternSplit(String strput,String regex){
    	 return strput.split(regex); 
    }
    
    public static String htmlEscapeText(String html){
    	return StringEscapeUtils.unescapeHtml(html);
    }
    
}
