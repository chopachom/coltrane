package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Developer;
import org.springframework.data.repository.CrudRepository;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 *
 * @author nik
 */
@Transactional(propagation = Propagation.MANDATORY)
public interface DeveloperRepository extends CrudRepository<Developer, Integer> {
}
