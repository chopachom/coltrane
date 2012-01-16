package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Application;
import org.springframework.data.repository.CrudRepository;

/**
 *
 * @author nik
 */
public interface ApplicationRepository extends CrudRepository<Application, Integer> {
}
