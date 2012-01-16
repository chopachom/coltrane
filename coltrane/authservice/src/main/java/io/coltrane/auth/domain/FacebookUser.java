package io.coltrane.auth.domain;

import java.util.Objects;
import javax.persistence.Column;
import javax.persistence.Entity;

/**
 *
 * @author nik
 */
@Entity
public class FacebookUser extends User {

    @Column(nullable = false, unique = true)
    private long facebookId;
    @Column(length = 512, nullable = false)
    private String accessToken;

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public long getFacebookId() {
        return facebookId;
    }

    public void setFacebookId(long facebookId) {
        this.facebookId = facebookId;
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
        final FacebookUser other = (FacebookUser) obj;
        if (this.facebookId != other.facebookId) {
            return false;
        }
        if (!Objects.equals(this.accessToken, other.accessToken)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 5;
        hash = 97 * hash + super.hashCode();
        hash = 97 * hash + (int) (this.facebookId ^ (this.facebookId >>> 32));
        hash = 97 * hash + Objects.hashCode(this.accessToken);
        return hash;
    }
}
