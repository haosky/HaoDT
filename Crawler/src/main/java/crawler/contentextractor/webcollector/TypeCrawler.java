package crawler.contentextractor.webcollector;

import cn.edu.hfut.dmic.webcollector.model.CrawlDatum;
import cn.edu.hfut.dmic.webcollector.model.CrawlDatums;
import cn.edu.hfut.dmic.webcollector.model.Links;
import cn.edu.hfut.dmic.webcollector.model.Page;
import cn.edu.hfut.dmic.webcollector.plugin.ram.RamCrawler;
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
import entity.GdgpoRecord;
import util.MongoUtil;
import org.jsoup.nodes.Element;

import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

/**
 * 
 * WebCollector 2.40新特性 page.matchType 在添加CrawlDatum时（添加种子、或在抓取时向next中添加任务），
 * 可以为CrawlDatum设置type信息
 * 
 * type的本质也是meta信息，为CrawlDatum的附加信息 在添加种子或向next中添加任务时，设置type信息可以简化爬虫的开发
 * 
 * 例如在处理列表页时，爬虫解析出内容页的链接，在将内容页链接作为后续任务
 * 将next中添加时，可设置其type信息为content（可自定义），在后续抓取中，
 * 通过page.matchType("content")就可判断正在解析的页面是否为内容页
 * 
 * 设置type的方法主要有3种： 1）添加种子时，addSeed(url,type)
 * 2）向next中添加后续任务时：next.add(url,type)或next.add(links,type)
 * 3）在定义CrawlDatum时：crawlDatum.type(type)
 *
 * @author huangzt
 */
public class TypeCrawler extends RamCrawler {

	int pageIndex = 1;
	int pageSize = 15;
	
	int i = 300;
	int maxi = 2994;
	
	int j = 300;
	int maxj = 2724;
	
	MongoClient mongoClient = null;
	
	public TypeCrawler() {
		mongoClient = MongoUtil.getMongoClient(true);
		MongoKit.INSTANCE.init(mongoClient, "gdgpo");
	}
	
	/*
	    该教程是DemoMetaCrawler的简化版
	    
	    该Demo爬虫需要应对豆瓣图书的三种页面：
	    1）标签页（taglist，包含图书列表页的入口链接）
	    2）列表页（booklist，包含图书详情页的入口链接）
	    3）图书详情页（content）
	
	    另一种常用的遍历方法可参考TutorialCrawler
	 */
	@Override
	public void visit(Page page, CrawlDatums next) {

		if (page.matchType("taglist")) {
			//如果是列表页，抽取内容页链接
			//将内容页链接的type设置为content，并添加到后续任务中
			Links links = page.getLinks("ul.m_m_c_list li>a");
			for (String link : links) {
				String tbl = "tcontent";
				long cnt = (new MongoQuery()).use(tbl).eq("url", link).count();
				if (cnt > 0) {
					break;
				}else{
					CrawlDatum datum = new CrawlDatum(link).type("booklist").meta("ftype", page.meta("ftype"));
					next.add(datum);
				}
			}
			
			//下一页
			if (page.meta("ftype").equals("采购公告")) {
				i++;
				if (i > maxi) {
					return;
				}
				
				String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
						+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
				String type = "taglist";
				
				long cnt = (new MongoQuery()).use(type).eq("url", url).count();
				
				while (cnt > 0) {
					cnt = (new MongoQuery()).use(type).eq("url", url).count();
					i++;
					if (i > maxi) {
						return;
					}
					url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
							+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
				}
				
				if (cnt == 0) {
					GdgpoRecord rec = new GdgpoRecord();
					rec.setFtype("采购公告");
					rec.setPagesize(i);
					rec.setUrl(url);
					(new MongoQuery()).use(type).set(rec).save();
					
					CrawlDatum datum = new CrawlDatum(url, type);
					datum.meta("ftype", "采购公告");
					next.add(datum);
				}
				
			}
			
			//下一页
			if (page.meta("ftype").equals("中标公告")) {
				j++;
				if (j > maxj) {
					return;
				}
				
				String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
						+ j + "&pageSize=" + pageSize + "&pointPageIndexId=" + (j - 1);
				String type = "taglist";
				
				long cnt = (new MongoQuery()).use(type).eq("url", url).count();
				
				while (cnt > 0) {
					cnt = (new MongoQuery()).use(type).eq("url", url).count();
					j++;
					if (j > maxj) {
						return;
					}
					url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
							+ j + "&pageSize=" + pageSize + "&pointPageIndexId=" + (j - 1);
				}
				
				if (cnt == 0) {
					GdgpoRecord rec = new GdgpoRecord();
					rec.setFtype("采购公告");
					rec.setPagesize(i);
					rec.setUrl(url);
					(new MongoQuery()).use(type).set(rec).save();
					
					CrawlDatum datum = new CrawlDatum(url, type);
					datum.meta("ftype", "中标公告");
					next.add(datum);
				}
				 
			}
			
			//next.add(page.getLinks("ul.m_m_c_list li>a"), "booklist");
			System.out.println("links:" + links);
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
				
				String tbl = "tcontent";
				
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
				String filePath = "D:/bigData/gdgpo/";
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
				
				if(page.content().length == 0){
					return;
				}
				
				FileUtils.write(fileName, page.content());
				
				//解释文件的文本，只解释word文本
				if(isWord){
					try {
						ByteArrayInputStream inputStream = new ByteArrayInputStream(page.content());
						Document doc = new Document(inputStream);
						//doc.save(fileNameTxt, SaveFormat.TEXT);
						//System.out.println("word content:" + doc.getText());
						
						String tbl = "fcontent";
						
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

	@Override
	public void stop() {
		super.stop();
		MongoKit.INSTANCE.getClient().close();
	}
	
	public static void main(String[] args) throws Exception {
		ClassLoader loader = Thread.currentThread().getContextClassLoader();
		InputStream license = new FileInputStream(loader.getResource("license.xml").getPath());// 凭证文件
		License aposeLic = new License();
		aposeLic.setLicense(license);
		
		TypeCrawler crawler = new TypeCrawler();
		//crawler.addSeed("https://book.douban.com/tag/","taglist");
		//crawler.addSeed("http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=-1&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=大数据&pageIndex=1&pageSize=15&pointPageIndexId=1","taglist");
		int pageIndex = 300;
		int pageSize = 15;
		//int maxPage = 8448;//8448
		
		//在抓取过程中再添加页码，避免种子太多爬虫出问题
		//for (int i = pageIndex; i <= 2994; i++) {
		for (int i = pageIndex; i <= 1; i++) {
			String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0005&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
					+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
			String type = "taglist";
			CrawlDatum datum = new CrawlDatum(url, type);
			datum.meta("ftype", "采购公告");
			crawler.addSeed(datum);
		}
		//for (int i = pageIndex; i <= 2724; i++) {
		for (int i = pageIndex; i <= 1; i++) {
			String url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=0008&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
					+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1);
			String type = "taglist";
			CrawlDatum datum = new CrawlDatum(url, type);
			datum.meta("ftype", "中标公告");
			crawler.addSeed(datum);
		}
		
		//Config.TIMEOUT_CONNECT = 3000;
		//Config.TIMEOUT_READ = 30000;
		
		/*for (int i = pageIndex; i <= maxPage; i++) {
			crawler.addSeed("http://www.gdgpo.gov.cn/queryMoreInfoList.do?channelCode=-1&issueOrgan=&operateDateFrom=&operateDateTo=&performOrgName=&purchaserOrgName=&regionIds=&sitewebId=4028889705bebb510105bec068b00003&sitewebName=广东省&stockIndexName=&stockNum=&stockTypes=&title=&pageIndex="
							+ i + "&pageSize=" + pageSize + "&pointPageIndexId=" + (i - 1),"taglist");
			//break;
		}*/

		/*可以设置每个线程visit的间隔，这里是毫秒*/
		//crawler.setVisitInterval(1000);
		/*可以设置http请求重试的间隔，这里是毫秒*/
		//crawler.setRetryInterval(1000);
		crawler.setTopN(500000);
		crawler.setThreads(50);
		crawler.start(500000);
	}

}
