package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Developer;
import org.springframework.data.repository.CrudRepository;

/**
 *
 * @author nik
 */
public interface DeveloperRepository extends CrudRepository<Developer, Integer> {
}
