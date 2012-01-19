package io.coltrane.auth.domain;

import java.util.Date;
import java.util.Objects;
import javax.persistence.*;

/**
 *
 * @author nik
 */
@Entity
public class ApplicationAsset {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    @Column(length = 4096, nullable = false)
    private String url;
    @Enumerated(EnumType.STRING)
    private ApplicationAssetType type;
    @Temporal(TemporalType.TIMESTAMP)
    private Date created = new Date(); // default value

    public Date getCreated() {
        return created;
    }

    public void setCreated(Date created) {
        this.created = created;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public ApplicationAssetType getType() {
        return type;
    }

    public void setType(ApplicationAssetType type) {
        this.type = type;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final ApplicationAsset other = (ApplicationAsset) obj;
        if (!Objects.equals(this.id, other.id)) {
            return false;
        }
        if (!Objects.equals(this.url, other.url)) {
            return false;
        }
        if (this.type != other.type) {
            return false;
        }
        if (!Objects.equals(this.created, other.created)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 53 * hash + Objects.hashCode(this.id);
        hash = 53 * hash + Objects.hashCode(this.url);
        hash = 53 * hash + (this.type != null ? this.type.hashCode() : 0);
        hash = 53 * hash + Objects.hashCode(this.created);
        return hash;
    }
}
