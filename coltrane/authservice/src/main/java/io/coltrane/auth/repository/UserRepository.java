package io.coltrane.auth.repository;

import io.coltrane.auth.domain.User;
import org.springframework.data.repository.Repository;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 *
 * @author nik
 */
@Transactional(propagation = Propagation.MANDATORY)
public interface UserRepository extends Repository<User, Integer> {

    User findByNickName(String nickName);
}
