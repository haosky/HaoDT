package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class Gdgpo {
	@JSONField(name = "gid")
	private String gid;
	@JSONField(name = "title")
	private String title;
	@JSONField(name = "qx")
	private String qx;
	@JSONField(name = "content")
	private String content;
	@JSONField(name = "links")
	private String links;
	@JSONField(name = "url")
	private String url;
	@JSONField(name = "fcontent")
	private String fcontent;
	
	@JSONField(name = "collecttime")
	private String collecttime;
	@JSONField(name = "namedentity")
	private String namedentity;
	@JSONField(name = "_id")
	private String id;

	@JSONField(name = "ftype")
	private String ftype;
	
	public String getFtype() {
		return ftype;
	}
	public void setFtype(String ftype) {
		this.ftype = ftype;
	}
	public String getGid() {
		return gid;
	}
	public void setGid(String gid) {
		this.gid = gid;
	}

	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}

	public String getNamedentity() {
		return namedentity;
	}
	public void setNamedentity(String namedentity) {
		this.namedentity = namedentity;
	}

	public String getQx() {
		return qx;
	}
	public void setQx(String qx) {
		this.qx = qx;
	}

	public String getContent() {
		return content;
	}
	public void setContent(String content) {
		this.content = content;
	}

	public String getLinks() {
		return links;
	}
	public void setLinks(String links) {
		this.links = links;
	}

	public String getCollecttime() {
		return collecttime;
	}
	public void setCollecttime(String collecttime) {
		this.collecttime = collecttime;
	}

	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}

	public String getFcontent() {
		return fcontent;
	}
	public void setFcontent(String fcontent) {
		this.fcontent = fcontent;
	}

	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}


}
