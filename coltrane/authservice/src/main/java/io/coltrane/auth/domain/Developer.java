package io.coltrane.auth.domain;

import java.util.List;
import java.util.Objects;
import javax.persistence.Entity;
import javax.persistence.OneToMany;

/**
 *
 * @author nik
 */
@Entity
public class Developer extends User {

    @OneToMany
    private List<DeveloperKey> keys;
    @OneToMany
    private List<Application> applications;

    public List<Application> getApplications() {
        return applications;
    }

    public void setApplications(List<Application> applications) {
        this.applications = applications;
    }

    public List<DeveloperKey> getKeys() {
        return keys;
    }

    public void setKeys(List<DeveloperKey> keys) {
        this.keys = keys;
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
        final Developer other = (Developer) obj;
        if (!Objects.equals(this.keys, other.keys)) {
            return false;
        }
        if (!Objects.equals(this.applications, other.applications)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 59 * hash + super.hashCode();
        hash = 89 * hash + Objects.hashCode(this.keys);
        hash = 89 * hash + Objects.hashCode(this.applications);
        return hash;
    }
}
