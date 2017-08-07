package crawler.contentextractor.webcollector;

import cn.edu.hfut.dmic.webcollector.model.CrawlDatum;
import cn.edu.hfut.dmic.webcollector.model.CrawlDatums;
import cn.edu.hfut.dmic.webcollector.model.Links;
import cn.edu.hfut.dmic.webcollector.model.Page;
import cn.edu.hfut.dmic.webcollector.plugin.berkeley.BreadthCrawler;
import cn.edu.hfut.dmic.webcollector.util.FileUtils;
import com.aspose.words.Document;
import com.aspose.words.License;
import com.cybermkd.mongo.kit.MongoKit;
import com.cybermkd.mongo.kit.MongoQuery;
import com.mongodb.MongoClient;
import com.xiaoleilu.hutool.date.DateUtil;
import com.xiaoleilu.hutool.io.FileUtil;
import crawler.contentextractor.ContentExtractor;
import entity.Gdgpo;
import util.MongoUtil;
import org.jsoup.nodes.Element;

import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;

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
public class GdgpoCrawler extends BreadthCrawler {
	
	public static String getNowTime(){
		Date now = new Date();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		String PaTime = dateFormat.format(now);
		return PaTime; 
	}
	
	String filePath = "D:/bigdata/Gdgpo/";
	
    /**
     * @param crawlPath crawlPath is the path of the directory which maintains
     * information of this crawler
     * @param autoParse if autoParse is true,BreadthCrawler will auto extract
     * links which match regex rules from pag
     */
    public GdgpoCrawler(String crawlPath, boolean autoParse) {
        super("crawl/" + crawlPath + "/", autoParse);
        this.filePath = filePath + crawlPath;
    }

	/*
	    可以往next中添加希望后续爬取的任务，任务可以是URL或者CrawlDatum
	    爬虫不会重复爬取任务，从2.20版之后，爬虫根据CrawlDatum的key去重，而不是URL
	    因此如果希望重复爬取某个URL，只要将CrawlDatum的key设置为一个历史中不存在的值即可
	    例如增量爬取，可以使用 爬取时间+URL作为key。
	
	    新版本中，可以直接通过 page.select(css选择器)方法来抽取网页中的信息，等价于
	    page.getDoc().select(css选择器)方法，page.getDoc()获取到的是Jsoup中的
	    Document对象，细节请参考Jsoup教程
	    
	  ==========================================================================  
	    该教程是DemoMetaCrawler的简化版
	    
	    该Demo爬虫需要应对豆瓣图书的三种页面：
	    1）标签页（taglist，包含图书列表页的入口链接）
	    2）列表页（booklist，包含图书详情页的入口链接）
	    3）图书详情页（content）
	
	    另一种常用的遍历方法可参考TutorialCrawler
	*/
    //@Override
    public void visit(Page page, CrawlDatums next) {
    	if (page.matchType("taglist")) {
			//如果是列表页，抽取内容页链接
			//将内容页链接的type设置为content，并添加到后续任务中
			next.add(page.getLinks("ul.m_m_c_list li>a"), "booklist");
			next.meta("ftype", page.meta("ftype"));
			
		} else if (page.matchType("booklist")) {
			/*next.add(page.getLinks("div.info>h2>a"),"content");*/
			try {
				Element doc = ContentExtractor.getContentElementByHtml(page.html(), page.url());
				String gid = UUID.randomUUID().toString();
				String title = page.select("div.zw_c_c_title").text();
				String qx = page.select("div.zw_c_c_qx").text();
				//String content = Jsoup.clean(doc.html(), Whitelist.none());
				String content = doc.text();
				Links links = page.getLinks("div.zw_c_cont a[href $=.doc]")
						.add(page.getLinks("div.zw_c_cont a[href $=.docx]"))
						.add(page.getLinks("div.zw_c_cont a[href $=.rar]"))
						.add(page.getLinks("div.zw_c_cont a[href $=.zip]"))
						.add(page.getLinks("div.zw_c_cont a[href $=.pdf]"));
				
				System.out.println("url:" + page.url()
						+ "\ngid:" + gid 
						+ "\ntitle:" + title 
						+ "\nqx:" + qx 
						+ "\ncontent:" + content
						+ "\nlinks:" + links.toString());
				
				String db = "gdgpo";
				String tbl = "tcontent";
				MongoClient mongoClient = MongoUtil.getMongoClient(true);
				MongoKit.INSTANCE.init(mongoClient, db);
				
				Gdgpo gdgpo = new Gdgpo();
				gdgpo.setUrl(page.url());
				gdgpo.setGid(gid);
				gdgpo.setTitle(title);
				gdgpo.setQx(qx);
				gdgpo.setContent(content);
				gdgpo.setLinks(links.toString());
				gdgpo.setCollecttime(DateUtil.now());
				gdgpo.setFtype(page.meta("ftype"));
				
				(new MongoQuery()).use(tbl).set(gdgpo).save();
				
				if (links.size()>0){
					//有文件的就去下载
					for (String url : links) {
						CrawlDatum datum = new CrawlDatum(url).type("filelist");
						datum.meta("url", page.url());
						datum.meta("gid", gid);
						datum.meta("title", title);
						datum.meta("qx", qx);
						datum.meta("content", content);
						datum.meta("links", links.toString());
						datum.meta("ftype", page.meta("ftype"));
						next.add(datum);
					}
				}
			} catch (Exception e) {
				//e.printStackTrace();
			}
		} else if (page.matchType("filelist")) {
			try {
				CrawlDatum datum = page.crawlDatum();
				boolean isWord = true;
				
				if(!page.url().toLowerCase().endsWith(".doc") && !page.url().toLowerCase().endsWith(".docx")){
					isWord = false;
				}

				if (!FileUtil.exist(filePath)) {
					FileUtil.mkdir(filePath);
				}
				
				String arr[] = page.url().split("/");
				String fileName = filePath + datum.meta("title") + "_" + arr[arr.length-1];
				//String fileNameTxt = fileName.substring(0, fileName.length()-4) +".txt";
				FileUtils.write(fileName, page.content());
				
				//解释文件的文本，只解释word文本
				if(isWord){
					try {
						ClassLoader loader = Thread.currentThread().getContextClassLoader();
						InputStream license = new FileInputStream(loader.getResource("license.xml").getPath());// 凭证文件
						License aposeLic = new License();
						aposeLic.setLicense(license);
						
						ByteArrayInputStream inputStream = new ByteArrayInputStream(page.content());
						Document doc = new Document(inputStream);
						//doc.save(fileNameTxt, SaveFormat.TEXT);
						//System.out.println("word content:" + doc.getText());
						
						String db = "gdgpo";
						String tbl = "fcontent";
						MongoClient mongoClient = MongoUtil.getMongoClient(true);
						MongoKit.INSTANCE.init(mongoClient, db);
						
						Gdgpo gdgpo = new Gdgpo();
						gdgpo.setUrl(page.url());
						gdgpo.setGid(datum.meta("gid"));
						gdgpo.setTitle(datum.meta("title"));
						gdgpo.setQx(datum.meta("qx"));
						gdgpo.setContent(datum.meta("content"));
						gdgpo.setLinks(datum.meta("links"));
						gdgpo.setFtype(datum.meta("ftype"));
						gdgpo.setCollecttime(DateUtil.now());
						gdgpo.setFcontent(doc.getText());
						
						(new MongoQuery()).use(tbl).set(gdgpo).save();
						
					} catch (Exception e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
				
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}else if (page.matchType("content")) {
			//处理内容页，抽取书名和豆瓣评分
			/*String title=page.select("h1>span").first().text();
			String score=page.select("strong.ll.rating_num").first().text();
			System.out.println("title:"+title+"\tscore:"+score);*/
		}
    }

    public static void main(String[] args) throws Exception {
    	GdgpoCrawler crawler = new GdgpoCrawler("www.gdgpo.gov.cn", false);
    	
    	int pageIndex = 1;
		int pageSize = 15;
		
		for (int i = pageIndex; i <= 2994; i++) {
			String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
					+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
			String type = "taglist";
			CrawlDatum datum = new CrawlDatum(url, type);
			datum.meta("ftype", "采购公告");

	    	crawler.addSeed(datum);
		}
		
		for (int i = pageIndex; i <= 2724; i++) {
			String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0008&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
					+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
			String type = "taglist";
			CrawlDatum datum = new CrawlDatum(url, type);
			datum.meta("ftype", "中标公告");
			
	    	crawler.addSeed(datum); 
		}
		

		/*start page*/
		/*url 种子*/
		//crawler.addSeed(u);
		/*添加URL正则约束*/
		//crawler.addRegex(u + ".*");
		/*do not fetch*/
		//crawler.addRegex("-.*\\.(jpg|png|gif|bmp|doc|xls|docx|xlsx|wps|pdf|rtf|rar|zip|js|css).*");
		/*do not fetch url contains #*/
		//crawler.addRegex("-.*#.*");
		
		/*设置线程数*/
		crawler.setThreads(15);
		/*设置每次迭代爬取的网页数量上限*/
		//crawler.setTopN(500000);
		/*设置是否断点爬取*/
		crawler.setResumable(true);
		/*start crawl with depth of 4*/
		/*开始爬取，迭代次数为depth*/
		crawler.start(5);

    }

}
