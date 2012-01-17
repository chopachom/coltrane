package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Application;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 *
 * @author nik
 */
@Transactional(propagation = Propagation.MANDATORY)
public interface ApplicationRepository extends CrudRepository<Application, Integer> {
    
    @Query("SELECT a FROM Application a WHERE a.author.nickName = :author AND a.appDomain = :appDomain")
    Application findByAuthorAndAppDomain(@Param("author") String author, @Param("appDomain") String appDomain);
}
