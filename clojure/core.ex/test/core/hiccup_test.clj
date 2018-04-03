(ns core.hiccup-test
  (:require [clojure.test :refer :all]
            [clojure.core.ex :refer :all]))

(deftest hiccup-test
  #_(testing "content filter"
    (is (= [1 2 3]
          (xfilter :n 3 [1 2 3 4 5 6 7])))
    (is (= [3 4 5]
          (xfilter :n 3 :st #(> % 2) [1 2 3 4 5 6 7])))
    (is (= [3 5 7]
          (xfilter :n 3 :st #(> % 2) :pred odd? [1 2 3 4 5 6 7 8 9 10 11])))
    (is (= [3 5 7]
          (xfilter :n 4 :st #(> % 2) :pred odd? :ed #(> % 8) [1 2 3 4 5 6 7 8 9 10 11])))     
  )
  
  (testing "cornner test"
    (let []
      (is (= nil
            (hiccup2clj nil)))))
)