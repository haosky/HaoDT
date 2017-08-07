package crawler.contentextractor.webcollector;

import cn.edu.hfut.dmic.webcollector.model.CrawlDatums;
import cn.edu.hfut.dmic.webcollector.model.Page;
import cn.edu.hfut.dmic.webcollector.plugin.berkeley.BreadthCrawler;
import cn.edu.hfut.dmic.webcollector.util.FileUtils;
import com.xiaoleilu.hutool.io.FileUtil;
import crawler.contentextractor.ContentExtractor;
import crawler.contentextractor.crawmodels.News;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * WebCollector 2.x版本的tutorial(2.20以上) 
 * 2.x版本特性：
 * 1）自定义遍历策略，可完成更为复杂的遍历业务，例如分页、AJAX
 * 2）可以为每个URL设置附加信息(MetaData)，利用附加信息可以完成很多复杂业务，例如深度获取、锚文本获取、引用页面获取、POST参数传递、增量更新等。
 * 3）使用插件机制，WebCollector内置两套插件。
 * 4）内置一套基于内存的插件（RamCrawler)，不依赖文件系统或数据库，适合一次性爬取，例如实时爬取搜索引擎。
 * 5）内置一套基于Berkeley DB（BreadthCrawler)的插件：适合处理长期和大量级的任务，并具有断点爬取功能，不会因为宕机、关闭导致数据丢失。 
 * 6）集成selenium，可以对javascript生成信息进行抽取
 * 7）可轻松自定义http请求，并内置多代理随机切换功能。 可通过定义http请求实现模拟登录。 
 * 8）使用slf4j作为日志门面，可对接多种日志
 *
 * 可在cn.edu.hfut.dmic.crawler.contentextractor.webcollector.example包中找到例子(Demo)
 *
 * @author huangzt
 */
public class NewsCrawler extends BreadthCrawler {
	
	public static String getNowTime(){
		Date now = new Date();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		String PaTime = dateFormat.format( now );
		return PaTime; 
	}
	
	String filePath = "E:/bigData/Govenment2016/";
	String siteName = "";
	
    /**
     * @param crawlPath crawlPath is the path of the directory which maintains
     * information of this crawler
     * @param autoParse if autoParse is true,BreadthCrawler will auto extract
     * links which match regex rules from pag
     */
    public NewsCrawler(String crawlPath, boolean autoParse, String siteName) {
        super("crawl/" + crawlPath + "/", autoParse);
        this.filePath = filePath + crawlPath;
        this.siteName = siteName;
    }

	/*
	    可以往next中添加希望后续爬取的任务，任务可以是URL或者CrawlDatum
	    爬虫不会重复爬取任务，从2.20版之后，爬虫根据CrawlDatum的key去重，而不是URL
	    因此如果希望重复爬取某个URL，只要将CrawlDatum的key设置为一个历史中不存在的值即可
	    例如增量爬取，可以使用 爬取时间+URL作为key。
	
	    新版本中，可以直接通过 page.select(css选择器)方法来抽取网页中的信息，等价于
	    page.getDoc().select(css选择器)方法，page.getDoc()获取到的是Jsoup中的
	    Document对象，细节请参考Jsoup教程
	*/
    @Override
    public void visit(Page page, CrawlDatums next) {
    	
		try {
			News news = ContentExtractor.getNewsByHtml(page.html(), page.url());
			
			String tpl = "URL:%s\r\n标题:%s\r\n时间:%s\r\n导航:%s\r\n采集时间:%s\r\n图片名:%s\r\n内容:\r\n来源：%s\r\n日期：%s\r\n%s\r\n\r\n原文地址：%s\r\n";
			String html = String.format(tpl, news.getUrl(), news.getTitle().replaceAll(" ", "").replaceAll("\\?", "").replaceAll("\\?", ""), news.getTime(), "", getNowTime(), "",
					siteName, news.getTime(), news.getContent().replaceAll("　　", "\r\n").replaceAll(" \\?", "").replaceAll("\\?", "").replaceAll("\\?", ""), news.getUrl());
			
			/*Pattern pattern = Pattern.compile("[\\?]");
			Matcher matcher = pattern.matcher(html);
			html = matcher.replaceAll("");*/
			
			// System.out.println(html);

			String fileName = news.getTitle().replaceAll("　", "");
			Pattern pattern = Pattern.compile("[\\s\\\\/:\\*\\?\\\"<>\\|]");
			Matcher matcher = pattern.matcher(fileName);
			fileName = matcher.replaceAll(""); // 将匹配到的非法字符以空替换

			FileUtils.write(this.filePath + "/" + fileName + ".txt", html, "GBK");

		} catch (Exception ex) {

		}
        
    }

    public static void main(String[] args) throws Exception {
		String filePath = "E:\\bigdata\\ting\\work\\";
    	String fileWeb = filePath + "website.txt";
    	
    	String website = FileUtils.read(fileWeb, "GBK");
    	String[] urls = website.split("\r\n");
    	List<String> lstUrl = new ArrayList<String>();
    	List<String> lstName = new ArrayList<String>();
    	List<String> lstPath = new ArrayList<String>();
    	
    	System.out.println(urls.length);
    	
    	for (String url : urls) {
			//System.out.println(url.split("\t")[1]);
			lstUrl.add(url.split("\t")[1]);
			
			//System.out.println(url.split("http://")[1].split("/")[0]);
			lstName.add(url.split("\t")[0]);
			lstPath.add(url.split("http://")[1].split("/")[0]);
		}

    	for (int i = 0; i < lstUrl.size(); i++) {
    		String u = lstUrl.get(i);
    		String n = lstName.get(i);
    		String p = lstPath.get(i);

			String checkPath = "E:/bigData/Govenment2016/" + n + "-" + p;
			if (FileUtil.exist(checkPath)) {
				continue;
			}

    		NewsCrawler crawler = new NewsCrawler(n + "-" + p, true, n);
    		
    		/*start page*/
    		/*url 种子*/
    		crawler.addSeed(u);
    		/*添加URL正则约束*/
    		crawler.addRegex(u + ".*");
    		/*do not fetch*/
    		crawler.addRegex("-.*\\.(jpg|png|gif|bmp|doc|xls|docx|xlsx|wps|pdf|rtf|rar|zip|js|css).*");
    		/*do not fetch url contains #*/
    		crawler.addRegex("-.*#.*");
    		
    		/*设置线程数*/
    		crawler.setThreads(50);
    		/*设置每次迭代爬取的网页数量上限*/
    		crawler.setTopN(50000);
    		/*设置是否断点爬取*/
    		crawler.setResumable(true);
    		/*start crawl with depth of 4*/
    		/*开始爬取，迭代次数为depth*/
    		crawler.start(50);
    		
		}

    }

}
