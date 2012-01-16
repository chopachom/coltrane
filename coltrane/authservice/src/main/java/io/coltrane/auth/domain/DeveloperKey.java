package io.coltrane.auth.domain;

import java.util.Objects;
import javax.persistence.*;

/**
 *
 * @author nik
 */
@Entity
public class DeveloperKey {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    @Column(length = 8128)
    private String sshKey;
    @Column(length = 512)
    private String sshHash;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getSshHash() {
        return sshHash;
    }

    public void setSshHash(String sshHash) {
        this.sshHash = sshHash;
    }

    public String getSshKey() {
        return sshKey;
    }

    public void setSshKey(String sshKey) {
        this.sshKey = sshKey;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final DeveloperKey other = (DeveloperKey) obj;
        if (!Objects.equals(this.id, other.id)) {
            return false;
        }
        if (!Objects.equals(this.sshKey, other.sshKey)) {
            return false;
        }
        if (!Objects.equals(this.sshHash, other.sshHash)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 41 * hash + Objects.hashCode(this.id);
        hash = 41 * hash + Objects.hashCode(this.sshKey);
        hash = 41 * hash + Objects.hashCode(this.sshHash);
        return hash;
    }
}
