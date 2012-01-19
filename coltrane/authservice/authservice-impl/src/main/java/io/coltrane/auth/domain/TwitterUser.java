package io.coltrane.auth.domain;

import java.util.Objects;
import javax.persistence.Column;
import javax.persistence.Entity;

/**
 *
 * @author nik
 */
@Entity
public class TwitterUser extends User {

    @Column(length = 512, nullable = false, unique = true)
    private String twitterName;
    @Column(nullable = false, unique = true)
    private long twitterId;
    @Column(length = 512, nullable = false)
    private String accessToken;
    @Column(length = 512, nullable = false)
    private String accessTokenSecret;

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getAccessTokenSecret() {
        return accessTokenSecret;
    }

    public void setAccessTokenSecret(String accessTokenSecret) {
        this.accessTokenSecret = accessTokenSecret;
    }

    public long getTwitterId() {
        return twitterId;
    }

    public void setTwitterId(long twitterId) {
        this.twitterId = twitterId;
    }

    public String getTwitterName() {
        return twitterName;
    }

    public void setTwitterName(String twitterName) {
        this.twitterName = twitterName;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        if (!super.equals(obj)) {
            return false;
        }
        final TwitterUser other = (TwitterUser) obj;
        if (!Objects.equals(this.twitterName, other.twitterName)) {
            return false;
        }
        if (this.twitterId != other.twitterId) {
            return false;
        }
        if (!Objects.equals(this.accessToken, other.accessToken)) {
            return false;
        }
        if (!Objects.equals(this.accessTokenSecret, other.accessTokenSecret)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 5;
        hash = 67 * hash + super.hashCode();
        hash = 67 * hash + Objects.hashCode(this.twitterName);
        hash = 67 * hash + (int) (this.twitterId ^ (this.twitterId >>> 32));
        hash = 67 * hash + Objects.hashCode(this.accessToken);
        hash = 67 * hash + Objects.hashCode(this.accessTokenSecret);
        return hash;
    }
}
