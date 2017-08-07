package entity;

import com.alibaba.fastjson.annotation.JSONField;

public class Congress {
	@JSONField(name = "collectTime")
	private String collecttime;
	@JSONField(name = "bt")
	private String bt;
	@JSONField(name = "nav")
	private String nav;
	@JSONField(name = "nr")
	private String nr;
	@JSONField(name = "strId")
	private String strid;
	@JSONField(name = "topic_name")
	private String topicName;
	@JSONField(name = "_id")
	private String id;
	@JSONField(name = "pic")
	private String pic;
	@JSONField(name = "topic_id")
	private String topicId;
	@JSONField(name = "uploadTime")
	private String uploadtime;
	@JSONField(name = "dataset")
	private String dataset;
	@JSONField(name = "url")
	private String url;

	public String getCollecttime() {
		return collecttime;
	}
	public void setCollecttime(String collecttime) {
		this.collecttime = collecttime;
	}

	public String getBt() {
		return bt;
	}
	public void setBt(String bt) {
		this.bt = bt;
	}

	public String getNav() {
		return nav;
	}
	public void setNav(String nav) {
		this.nav = nav;
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

	public String getPic() {
		return pic;
	}
	public void setPic(String pic) {
		this.pic = pic;
	}

	public String getTopicId() {
		return topicId;
	}
	public void setTopicId(String topicId) {
		this.topicId = topicId;
	}

	public String getUploadtime() {
		return uploadtime;
	}
	public void setUploadtime(String uploadtime) {
		this.uploadtime = uploadtime;
	}

	public String getDataset() {
		return dataset;
	}
	public void setDataset(String dataset) {
		this.dataset = dataset;
	}

	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}

}