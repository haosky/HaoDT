package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class Govenmentnew {
	@JSONField(name = "collectTime")
	private String collecttime;
	@JSONField(name = "nav")
	private String nav;
	@JSONField(name = "namedentity")
	private String namedentity;
	@JSONField(name = "nr")
	private String nr;
	@JSONField(name = "strId")
	private String strid;
	@JSONField(name = "pic")
	private String pic;
	@JSONField(name = "uploadTime")
	private String uploadtime;
	@JSONField(name = "url")
	private String url;
	@JSONField(name = "bt")
	private String bt;
	@JSONField(name = "topic_name")
	private String topicName;
	@JSONField(name = "_id")
	private String id;
	@JSONField(name = "topic_id")
	private String topicId;
	@JSONField(name = "dataset")
	private String dataset;

	public String getCollecttime() {
		return collecttime;
	}
	public void setCollecttime(String collecttime) {
		this.collecttime = collecttime;
	}

	public String getNav() {
		return nav;
	}
	public void setNav(String nav) {
		this.nav = nav;
	}

	public String getNamedentity() {
		return namedentity;
	}
	public void setNamedentity(String namedentity) {
		this.namedentity = namedentity;
	}

	public String getNr() {
		return nr;
	}
	public void setNr(String nr) {
		this.nr = nr;
	}

	public String getStrid() {
		return strid;
	}
	public void setStrid(String strid) {
		this.strid = strid;
	}

	public String getPic() {
		return pic;
	}
	public void setPic(String pic) {
		this.pic = pic;
	}

	public String getUploadtime() {
		return uploadtime;
	}
	public void setUploadtime(String uploadtime) {
		this.uploadtime = uploadtime;
	}

	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}

	public String getBt() {
		return bt;
	}
	public void setBt(String bt) {
		this.bt = bt;
	}

	public String getTopicName() {
		return topicName;
	}
	public void setTopicName(String topicName) {
		this.topicName = topicName;
	}

	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}

	public String getTopicId() {
		return topicId;
	}
	public void setTopicId(String topicId) {
		this.topicId = topicId;
	}

	public String getDataset() {
		return dataset;
	}
	public void setDataset(String dataset) {
		this.dataset = dataset;
	}

}