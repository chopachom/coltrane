package io.coltrane.auth.repository;

import io.coltrane.auth.domain.FacebookUser;
import org.springframework.data.repository.CrudRepository;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 *
 * @author nik
 */
@Transactional(propagation = Propagation.MANDATORY)
public interface FacebookUserRepository extends CrudRepository<FacebookUser, Integer> {
}
