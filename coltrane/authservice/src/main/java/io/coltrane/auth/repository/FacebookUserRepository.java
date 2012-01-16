package io.coltrane.auth.repository;

import io.coltrane.auth.domain.FacebookUser;
import org.springframework.data.repository.CrudRepository;

/**
 *
 * @author nik
 */
public interface FacebookUserRepository extends CrudRepository<FacebookUser, Integer> {
}
