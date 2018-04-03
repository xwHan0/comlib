(ns 
  ^{:doc 
    "
  * cum: Accumulatively calculate by function f and get a sequence.
  * update: Read, delete and modify collection function."}
  clojure.core.seq-func-extend)

      
;=====================================================================================================
;====  sequential function extend
;=====================================================================================================

(def ^:private PARAM-% 
  {(quote %0) 0
   (quote %1) 1
   (quote %2) 2
   (quote %3) 3
   (quote %4) 4
   (quote %5) 5
   (quote %6) 6
   (quote %7) 7
   (quote %8) 8
   (quote %9) 9})

(defn coll-merge [& colls] (apply map vector colls))
  
(defmacro func-parse
  [[pred & args]]
  (let [cs (gensym "cs")]
    (list 'fn [cs]
      (cons pred
        (map 
          (fn [arg] 
            (if-let [idx (get PARAM-% arg)] 
              `(get ~cs ~idx) 
              (if (= arg (quote %))
                cs
                arg)))
          args)))))
  
  
(defmacro seq-func-extend
  [func & bypass]
  (let [coll-sym2 (gensym "coll")
        pred-sym2 (gensym "pred")
        args-sym2 (gensym "args")
        sym-l-f (symbol (str "_l" (name func)))
        pred-sym (gensym "pred")
        ofmt-sym (gensym "ofmt")
        colls-sym (gensym "colls")
        rst-sym (gensym "rst")
        pred-sym1 (gensym "pred")
        ofmt-sym1 (gensym "ofmt")
        args-sym (gensym "args")
        sym-l-f `(fn [~pred-sym ~ofmt-sym ~@bypass & ~colls-sym]
                   (let [~rst-sym (~func #(apply ~pred-sym %) ~@bypass (apply coll-merge ~colls-sym))]
                      (cond (= :REDUCE-LAST ~ofmt-sym) (map last ~rst-sym)
                            (= :REDUCE-FIRST ~ofmt-sym) (map first ~rst-sym)
                            :else ~rst-sym)))]
    `(let []
       (defn ~(symbol (str "f" (name func))) [~coll-sym2 ~pred-sym2 ~@bypass & ~args-sym2]
         (~func #(apply ~pred-sym2 % ~args-sym2) ~@bypass ~coll-sym2))
       (defn ~(symbol (str "l" (name func))) [~pred-sym1 ~ofmt-sym1 ~@bypass & ~args-sym]
         (if (or (= ~ofmt-sym1 :REDUCE-LAST) (= ~ofmt-sym1 :REDUCE-FIRST) (= ~ofmt-sym1 :REDUCE-WHOLE))
           (apply ~sym-l-f ~pred-sym1 ~ofmt-sym1 ~args-sym)
           (apply ~sym-l-f ~pred-sym1 :REDUCE-FIRST ~ofmt-sym1 ~args-sym))))))

(defmacro pred-proc
  ([func pred-form & colls]
    (let [ofmt (last colls)
          rst (if (keyword? ofmt)
                `(~func (func-parse ~pred-form) (coll-merge ~@(butlast colls)))
                `(~func (func-parse ~pred-form) (coll-merge ~@colls)))
          ofmt (if (keyword? ofmt) ofmt :REDUCE-FIRST)]
       (cond (= :REDUCE-LAST ofmt) `(map last ~rst)
             (= :REDUCE-FIRST ofmt) `(map first ~rst)
             :else rst))))

